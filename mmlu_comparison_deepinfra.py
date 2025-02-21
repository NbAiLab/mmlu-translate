#!/usr/bin/env python3
import os
import json
import argparse
import re
import threading
import logging
from openai import OpenAI
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

# Global variable for accumulating estimated cost.
total_cost = 0.0
cost_lock = threading.Lock()

# Thread-local storage for the API client.
_thread_local = threading.local()


def get_client(api_key):
    if not hasattr(_thread_local, "client"):
        _thread_local.client = OpenAI(api_key=api_key, base_url="https://api.deepinfra.com/v1/openai")
    return _thread_local.client


def accumulate_stream_response(response):
    full_text = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        full_text += delta.get("content", "")
    return full_text.strip(), ""


def parse_api_response(text):
    """
    Attempt to extract a JSON object from the API response text.
    Looks for the first '{' and the last '}' and attempts to parse the substring.
    """
    text = text.strip()
    text = re.sub("<think>.*?</think>", "", text, flags=re.DOTALL)
    if text.startswith("```"):
        text = text.strip("`").strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_text = text[start:end + 1]
        return json.loads(json_text)
    raise ValueError("No valid JSON object found in text.")


def process_record(english_line, norwegian_line, template, api_key, stream_output, model):
    global total_cost
    error_reason = None
    try:
        eng_record = json.loads(english_line.strip())
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed for English line: {english_line.strip()} with error: {e}")
        return None

    try:
        nor_record = json.loads(norwegian_line.strip())
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed for Norwegian line: {norwegian_line.strip()} with error: {e}")
        return None

    # Required keys for both records.
    required_keys = ["sample_id", "question", "option_a", "option_b", "option_c", "option_d"]

    for key in required_keys:
        if key not in eng_record:
            logging.warning(f"English record skipped because it lacks '{key}' key: {eng_record}")
            return None
        if key not in nor_record:
            logging.warning(f"Norwegian record skipped because it lacks '{key}' key: {nor_record}")
            return None

    # Prepare the parts for the prompt.
    english_prompt_data = {
        "question": eng_record["question"],
        "option_a": eng_record["option_a"],
        "option_b": eng_record["option_b"],
        "option_c": eng_record["option_c"],
        "option_d": eng_record["option_d"]
    }
    norwegian_prompt_data = {
        "question": nor_record["question"],
        "option_a": nor_record["option_a"],
        "option_b": nor_record["option_b"],
        "option_c": nor_record["option_c"],
        "option_d": nor_record["option_d"]
    }

    # Replace placeholders in the evaluation template.
    user_prompt = template.replace("{english_question}", json.dumps(english_prompt_data, ensure_ascii=False))
    user_prompt = user_prompt.replace("{norwegian_question}", json.dumps(norwegian_prompt_data, ensure_ascii=False))

    client = get_client(api_key)
    try:
        error_reason = "API call failed."
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": user_prompt},
            ],
            stream=stream_output,
            max_tokens=8192,
        )

        error_reason = f"Failed to extract evaluation for prompt: {user_prompt}"
        if stream_output:
            final_text, _ = accumulate_stream_response(response)
        else:
            message = response.choices[0].message
            final_text = message.content.strip() if message.content else ""
        # Accumulate estimated cost if provided.
        if hasattr(response, "usage") and response.usage is not None:
            estimated_cost = getattr(response.usage, "estimated_cost", 0.0)
        else:
            estimated_cost = 0.0
        with cost_lock:
            total_cost += float(estimated_cost)

        error_reason = "API response not valid JSON."
        output_data = parse_api_response(final_text)

        error_reason = "Missing evaluation keys in output data."
        # Ensure the output contains the required structure.
        # Force the original id from the English record.
        output_data["id"] = eng_record["sample_id"]
        # Expecting output_data to have "score" and "reason".
        return json.dumps(output_data, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Record processing failed with error: {e}, reason: {error_reason}")
        error_output = {key: eng_record.get(key, "N/A") for key in required_keys}
        error_output["id"] = eng_record.get("sample_id", "N/A")
        error_output["score"] = 0
        error_output["reason"] = error_reason
        return json.dumps(error_output, ensure_ascii=False)


def process_file_parallel(english_file, norwegian_file, template, output_file, api_key, stream_output, num_workers, write_immediately, model):
    processed_count = 0
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as out_f:
            processed_count = sum(1 for _ in out_f)
    logging.info(f"Already processed {processed_count} record pairs in output file {output_file}")

    with open(english_file, "r", encoding="utf-8") as eng_f:
        eng_lines = eng_f.readlines()
    with open(norwegian_file, "r", encoding="utf-8") as nor_f:
        nor_lines = nor_f.readlines()

    total_pairs = min(len(eng_lines), len(nor_lines))
    if len(eng_lines) != len(nor_lines):
        logging.warning("The English and Norwegian files have different number of lines. Processing will use the minimum count.")

    logging.info(f"Total record pairs in input files: {total_pairs}")
    eng_lines_to_process = eng_lines[processed_count:total_pairs]
    nor_lines_to_process = nor_lines[processed_count:total_pairs]
    total_to_process = len(eng_lines_to_process)
    logging.info(f"Record pairs to process in this run: {total_to_process}")
    if total_to_process == 0:
        logging.info("No new record pairs to process.")
        return

    results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor, \
         open(output_file, "a", encoding="utf-8") as out_file:
        for processed in tqdm(
                executor.map(process_record, eng_lines_to_process, nor_lines_to_process,
                             repeat(template), repeat(api_key), repeat(stream_output), repeat(model)),
                total=total_to_process,
                desc="Processing record pairs"
        ):
            if processed is not None:
                if write_immediately:
                    out_file.write(processed + "\n")
                    out_file.flush()
                else:
                    results.append(processed)
        if not write_immediately:
            for record in results:
                out_file.write(record + "\n")


def load_template(template_file):
    try:
        with open(template_file, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Failed to load template from {template_file} with error: {e}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate translation quality between English and Norwegian JSON-lines files using DeepSeek API."
    )
    parser.add_argument("--english_file", required=True, help="Input English JSON-lines file.")
    parser.add_argument("--norwegian_file", required=True, help="Input Norwegian JSON-lines file.")
    parser.add_argument("--template_file", default="templates/evaluation_template.txt",
                        help="Evaluation template file (default: templates/evaluation_template.txt).")
    parser.add_argument("--output_file", required=True,
                        help="Output JSON-lines file for evaluation results (e.g., comparison.jsonl).")
    parser.add_argument("--processes", type=int, default=50, help="Number of parallel workers (default: 50).")
    parser.add_argument("--model", default="deepseek-ai/DeepSeek-R1", help="Model to use (default: deepseek-ai/DeepSeek-R1).")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging output.")
    args = parser.parse_args()

    # Configure logging based on the --debug flag.
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    api_key = os.getenv("DEEP_INFRA")
    if not api_key:
        raise EnvironmentError("DEEP_INFRA environment variable not set.")

    # Ensure the output folder exists.
    output_folder = os.path.dirname(args.output_file)
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    template_content = load_template(args.template_file)

    process_file_parallel(
        english_file=args.english_file,
        norwegian_file=args.norwegian_file,
        template=template_content,
        output_file=args.output_file,
        api_key=api_key,
        stream_output=False,
        num_workers=args.processes,
        write_immediately=True,
        model=args.model
    )

    print(f"Total estimated cost: {total_cost:.8f}")
