#!/usr/bin/env python3
import os
import json
import argparse
import threading
import logging
from openai import OpenAI
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

# Global variables for accumulating cost.
total_cost = 0.0
cost_lock = threading.Lock()

# Thread-local storage for the API client.
_thread_local = threading.local()

def get_client(api_key):
    if not hasattr(_thread_local, "client"):
        _thread_local.client = OpenAI(api_key=api_key, base_url="https://api.deepinfra.com/v1/openai")
    return _thread_local.client

def accumulate_stream_response(response):
    # Simply accumulate all content and return the final text.
    full_text = ""
    for chunk in response:
        delta = chunk.choices[0].delta
        full_text += delta.get("content", "")
    return full_text.strip(), ""

def parse_api_response(text):
    """
    Attempt to extract a JSON object from the API response text.
    This function looks for the first '{' and the last '}' and attempts to parse the substring.
    """
    text = text.strip()
    # Remove markdown code block markers if present.
    if text.startswith("```"):
        text = text.strip("`").strip()
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_text = text[start:end+1]
        return json.loads(json_text)
    raise ValueError("No valid JSON object found in text.")

def process_record(line, template, api_key, stream_output):
    global total_cost
    try:
        input_data = json.loads(line.strip())
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding failed for line: {line.strip()} with error: {e}")
        return None

    # Ensure required fields are present.
    for key in ["question", "subject", "choices", "answer"]:
        if key not in input_data:
            logging.warning(f"Record skipped because it lacks '{key}' key: {input_data}")
            return None

    # Extract original fields.
    original_question = input_data["question"]
    original_subject = input_data["subject"]
    original_choices = input_data["choices"]
    original_answer = input_data["answer"]
    original_id = input_data.get("id", None)

    # Create prompt by replacing {question} in the template.
    user_prompt = template.replace("{question}", original_question)
    client = get_client(api_key)

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=[
                {"role": "system", "content": ""},
                {"role": "user", "content": user_prompt},
            ],
            stream=stream_output,
            max_tokens=2000
        )
    except Exception as e:
        logging.error(f"API call failed for prompt: {user_prompt} with error: {e}")
        error_output = {
            "id": original_id if original_id is not None else "N/A",
            "question": "ERROR: Failed to get response from API",
            "subject": original_subject,
            "choices": original_choices,
            "answer": original_answer,
            "Reason": "API call failed",
            "Score": 0
        }
        return json.dumps(error_output, ensure_ascii=False)

    try:
        if stream_output:
            final_text, _ = accumulate_stream_response(response)
        else:
            message = response.choices[0].message
            final_text = message.content.strip() if message.content else ""
        # Extract and accumulate estimated cost.
        if hasattr(response, "usage") and response.usage is not None:
            estimated_cost = getattr(response.usage, "estimated_cost", 0.0)
        else:
            estimated_cost = 0.0
        with cost_lock:
            total_cost += float(estimated_cost)
    except Exception as e:
        logging.error(f"Failed to extract answer for prompt: {user_prompt} with error: {e}")
        error_output = {
            "id": original_id if original_id is not None else "N/A",
            "question": "ERROR: Failed to extract final answer",
            "subject": original_subject,
            "choices": original_choices,
            "answer": original_answer,
            "Reason": "Failed to extract final answer",
            "Score": 0
        }
        return json.dumps(error_output, ensure_ascii=False)

    try:
        output_data = parse_api_response(final_text)
    except Exception as e:
        logging.error(f"Failed to parse API response as JSON: {final_text} with error: {e}")
        output_data = {
            "id": original_id if original_id is not None else "N/A",
            "question": "ERROR: API response not valid JSON",
            "subject": original_subject,
            "choices": original_choices,
            "answer": original_answer,
            "Reason": "API response not valid JSON",
            "Score": 0
        }
        return json.dumps(output_data, ensure_ascii=False)

    # Override fields that must not be changed.
    output_data["id"] = original_id if original_id is not None else "N/A"
    output_data["subject"] = original_subject
    output_data["answer"] = original_answer
    if "choices" not in output_data:
        output_data["choices"] = original_choices

    # Expected output structure:
    # {
    #   "id": (unchanged),
    #   "question": (translated question),
    #   "subject": (unchanged),
    #   "choices": (translated choices),
    #   "answer": (unchanged integer 1-4),
    #   "Reason": (explanation on translation choices and challenges),
    #   "Score": (integer from 1 to 5 evaluating the translation)
    # }
    return json.dumps(output_data, ensure_ascii=False)

def process_file_parallel(input_file, template, output_file, api_key, stream_output, num_workers, write_immediately):
    processed_count = 0
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as out_f:
            processed_count = sum(1 for _ in out_f)
    logging.info(f"Already processed {processed_count} records in output file {output_file}")

    with open(input_file, "r", encoding="utf-8") as in_f:
        lines = in_f.readlines()
    total_lines = len(lines)
    logging.info(f"Total records in input file: {total_lines}")
    lines_to_process = lines[processed_count:]
    total = len(lines_to_process)
    logging.info(f"Records to process in this run: {total}")
    if total == 0:
        logging.info("No new records to process.")
        return

    if write_immediately:
        out_file = open(output_file, "a", encoding="utf-8")
    else:
        results = []
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        for processed in tqdm(
            executor.map(process_record, lines_to_process, repeat(template), repeat(api_key), repeat(stream_output)),
            total=total,
            desc="Processing"
        ):
            if processed is not None:
                if write_immediately:
                    out_file.write(processed + "\n")
                    out_file.flush()
                else:
                    results.append(processed)
    if not write_immediately:
        with open(output_file, "a", encoding="utf-8") as out_f:
            for record in results:
                out_f.write(record + "\n")
    else:
        out_file.close()

def load_template(template_file):
    try:
        with open(template_file, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logging.error(f"Failed to load template from {template_file} with error: {e}")
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON-lines with DeepSeek API in parallel.")
    parser.add_argument("--input_file", required=True, help="Input JSON-lines file.")
    parser.add_argument("--template_file", default="templates/norwegian_template.txt",
                        help="Optional template file. Defaults to 'templates/norwegian_template.txt'.")
    parser.add_argument("--output_folder", default="translated_data/",
                        help="Optional output folder to save the output file. Defaults to 'translated_data/'.")
    parser.add_argument("--processes", type=int, default=10, help="Number of parallel workers (default: 10).")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging output.")
    args = parser.parse_args()

    # Configure logging based on the --debug flag.
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    api_key = os.getenv("DEEP_INFRA")
    if not api_key:
        raise EnvironmentError("DEEP_INFRA environment variable not set.")

    # Ensure the output folder exists.
    os.makedirs(args.output_folder, exist_ok=True)

    template_content = load_template(args.template_file)
    # Use the same filename for output as the input file, placed in the output folder.
    output_file = os.path.join(args.output_folder, os.path.basename(args.input_file))

    process_file_parallel(
        input_file=args.input_file,
        template=template_content,
        output_file=output_file,
        api_key=api_key,
        stream_output=False,  # Always false
        num_workers=args.processes,
        write_immediately=True  # Always true
    )

    # Print the total estimated cost after processing all records.
    print(f"Total estimated cost: {total_cost:.8f}")
