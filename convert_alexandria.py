#!/usr/bin/env python3
import os
import json
import pandas as pd
import argparse

def convert_structure(structure_file, alexandria_file, output_file):
    # Load the entire Alexandria data into a DataFrame (one JSON object per line)
    alex_df = pd.read_json(alexandria_file, lines=True)
    # Build a lookup dict: key = Alexandria "id", value = row as dict
    alex_lookup = alex_df.set_index("id").to_dict(orient="index")
    
    with open(structure_file, "r", encoding="utf-8") as struct_in, \
         open(output_file, "w", encoding="utf-8") as out:
        for line in struct_in:
            line = line.strip()
            if not line:
                continue
            try:
                structure_entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            
            sample_id = structure_entry.get("sample_id")
            if not sample_id:
                continue
            
            # Find matching entry in Alexandria data (match sample_id to Alexandria id)
            alex_entry = alex_lookup.get(sample_id)
            if alex_entry is None:
                continue
            
            # Build the new entry:
            # - "sample_id", "subject", "subject_category" are taken from the structure entry.
            # - "question", "option_a", "option_b", "option_c", "option_d", "answer" come from alex_entry.
            # - The rest are set to default values.
            new_entry = {
                "sample_id": structure_entry.get("sample_id"),
                "subject": structure_entry.get("subject"),
                "subject_category": structure_entry.get("subject_category"),
                "question": alex_entry.get("instruction", ""),
                "option_a": alex_entry.get("option_a", ""),
                "option_b": alex_entry.get("option_b", ""),
                "option_c": alex_entry.get("option_c", ""),
                "option_d": alex_entry.get("option_d", ""),
                "answer": alex_entry.get("answer", ""),
                "required_knowledge": "[]",
                "time_sensitive": "[]",
                "reference": "[]",
                "culture": "[]",
                "region": "[]",
                "country": "[]",
                "cultural_sensitivity_label": "-",
                "is_annotated": False
            }
            out.write(json.dumps(new_entry) + "\n")
    
    print(f"Conversion complete. Output written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert Alexandria JSONL file to the structure defined by a given structure JSONL file."
    )
    parser.add_argument("--structure_file", required=True,
                        help="Path to the structure JSONL file (e.g., mmlu-no-best-clean/n1.jsonl)")
    parser.add_argument("--alexandria_file", required=True,
                        help="Path to the Alexandria JSONL file (e.g., alexandria_data/all.jsonl)")
    parser.add_argument("--output_file", required=True,
                        help="Path to the output JSONL file")
    args = parser.parse_args()
    
    convert_structure(args.structure_file, args.alexandria_file, args.output_file)
