import argparse
import json
import os
import re
from pathlib import Path

import pandas as pd


def main(input_files, output_folder):
    for file in input_files:
        file = Path(file)
        with open(file, "r", encoding="utf-8") as in_f:
            data = [json.loads(line) for line in in_f]
        file_name = file.stem
        file_name = re.sub(r"_(train|dev|test|val|validation)", "", file_name).strip()

        df = pd.DataFrame(data)
        # sample_id structure is subject/split/counter
        splits = df["sample_id"].str.split("/", expand=True).iloc[:, 1].unique()
        for split in splits:
            split_df = df[df["sample_id"].str.contains(split)]
            out_name = f"{split}-00000-of-00001.parquet"
            out_file = os.path.join(output_folder, file_name, out_name)
            os.makedirs(os.path.dirname(out_file), exist_ok=True)
            split_df.to_parquet(out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--input_files", nargs='+', help="Input files")
    parser.add_argument("--output_folder", type=str, default="data/", help="Output folder")
    args = parser.parse_args()

    main(
        input_files=args.input_files,
        output_folder=args.output_folder
    )
