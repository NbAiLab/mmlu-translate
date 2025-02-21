import os
import json
import pandas as pd
import argparse
from collections import defaultdict

def process_files(input_directory, output_file=None):
    # Extract models from filenames
    files = [f for f in os.listdir(input_directory) if f.startswith("comparison_") and f.endswith(".jsonl")]
    
    # Create a dictionary to store scores
    data = defaultdict(lambda: defaultdict(list))
    
    for file in files:
        # Extract model names from filename
        parts = file.replace("comparison_", "").replace(".jsonl", "").split("_by_")
        translation_model = parts[0]
        evaluation_model = parts[1]
        
        scores = []
        with open(os.path.join(input_directory, file), "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                score = entry.get("score")
                if isinstance(score, (int, float)) and 1 <= score <= 5:
                    scores.append(score)
        
        if scores:
            avg_score = sum(scores) / len(scores)
        else:
            avg_score = None
        
        data[translation_model][evaluation_model] = avg_score
    
    # Convert to DataFrame
    models = sorted(set(data.keys()) | {m for d in data.values() for m in d})
    df = pd.DataFrame(index=models, columns=models)
    
    for t_model in data:
        for e_model in data[t_model]:
            df.loc[t_model, e_model] = round(data[t_model][e_model], 2) if data[t_model][e_model] is not None else "N/A"
    
    # Compute average performance of translations (row-wise mean)
    avg_translation_performance = df.apply(pd.to_numeric, errors='coerce').mean(axis=1).round(2)
    avg_translation_table = pd.DataFrame(avg_translation_performance, columns=["Average Translation Score"])
    
    # Compute strictness in evaluation (column-wise mean)
    evaluation_strictness = df.apply(pd.to_numeric, errors='coerce').mean(axis=0).round(2)
    strictness_table = pd.DataFrame(evaluation_strictness, columns=["Evaluation Strictness"])
    
    # Save as CSV if specified
    if output_file:
        df.to_csv(output_file)
    
    # Print as Markdown tables
    print("### Translation Quality Table")
    print(df.to_markdown())
    print("\n### Average Performance Translations")
    print(avg_translation_table.to_markdown())
    print("\n### Strictness in Evaluating Translations")
    print(strictness_table.to_markdown())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process MMLU comparison JSONL files.")
    parser.add_argument("--input_directory", default="experiment_compare/", help="Directory containing comparison JSONL files.")
    parser.add_argument("--output_file", required=False, help="Optional CSV output file.")
    
    args = parser.parse_args()
    
    process_files(args.input_directory, args.output_file)

