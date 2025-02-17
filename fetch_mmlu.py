#!/usr/bin/env python3
import argparse
import json
import logging
import os
from datasets import load_dataset

def fetch_dataset(split: str, dataset_name: str = "cais/mmlu", config: str = "all"):
    logging.debug(f"Loading dataset '{dataset_name}' with config '{config}' and split '{split}'")
    dataset = load_dataset(dataset_name, config, split=split)
    logging.debug(f"Loaded dataset with {len(dataset)} records for config '{config}' and split '{split}'")
    return dataset

def save_jsonl(dataset, output_file: str):
    logging.debug(f"Saving dataset to '{output_file}' with added id field")
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, record in enumerate(dataset):
            # Create a new record with 'id' as the first key
            new_record = {"id": idx}
            new_record.update(record)
            f.write(json.dumps(new_record) + "\n")
    logging.debug(f"Finished saving dataset to '{output_file}'")

def main():
    parser = argparse.ArgumentParser(
        description="Fetch the MMLU test, validation, and dev sets (using the default config 'all') from HuggingFace and save them as JSONL files with an added id field."
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default="data/",
        help="Path to the output folder. Default is 'data/'."
    )
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Ensure the output folder exists
    os.makedirs(args.output_folder, exist_ok=True)
    
    config_name = "all"  # Default config to avoid the ValueError

    # Fetch and save test set
    test_dataset = fetch_dataset(split="test", config=config_name)
    test_output_file = os.path.join(args.output_folder, "test.jsonl")
    save_jsonl(test_dataset, test_output_file)

    # Fetch and save validation set
    validation_dataset = fetch_dataset(split="validation", config=config_name)
    validation_output_file = os.path.join(args.output_folder, "validation.jsonl")
    save_jsonl(validation_dataset, validation_output_file)
    
    # Fetch and save dev set
    dev_dataset = fetch_dataset(split="dev", config=config_name)
    dev_output_file = os.path.join(args.output_folder, "dev.jsonl")
    save_jsonl(dev_dataset, dev_output_file)

if __name__ == '__main__':
    main()
