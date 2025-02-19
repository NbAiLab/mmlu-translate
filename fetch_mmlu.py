#!/usr/bin/env python3
import argparse
import json
import logging
import os
from datasets import load_dataset, get_dataset_config_names, get_dataset_split_names


def fetch_dataset(dataset_id: str, split: str, config: str = "all"):
    logging.debug(f"Loading dataset '{dataset_id}' with config '{config}' and split '{split}'")
    dataset = load_dataset(dataset_id, config, split=split)
    logging.debug(f"Loaded dataset with {len(dataset)} records for config '{config}' and split '{split}'")
    return dataset


def save_jsonl(dataset, output_file: str, add_id_field: bool = False):
    logging.debug(f"Saving dataset to '{output_file}' with added id field")
    with open(output_file, "w", encoding="utf-8") as f:
        for idx, record in enumerate(dataset):
            # Create a new record with 'id' as the first key
            new_record = {"id": idx} if add_id_field else {}
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

    dataset_id = "CohereForAI/Global-MMLU"
    dataset_name = dataset_id.split("/")[-1]
    for config_name in get_dataset_config_names(dataset_id):
        for split in get_dataset_split_names(dataset_id, config_name):
            dataset = fetch_dataset(dataset_id, split, config_name)
            output_file = os.path.join(args.output_folder, f"{dataset_name}_{split}_{config_name}.jsonl")
            save_jsonl(dataset, output_file)


if __name__ == '__main__':
    main()
