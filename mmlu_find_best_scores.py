import os
import json
import argparse
from collections import defaultdict

def process_files(input_folder, output_folder):
    # List all relevant files from input_folder
    files = [
        f for f in os.listdir(input_folder)
        if f.startswith("comparison_") and f.endswith(".jsonl") and "Alexandria" not in f
    ]
    
    # Global dictionary to track best scores across all files.
    # Use a set for models to ensure uniqueness.
    global_best_scores = defaultdict(lambda: {"score": float('-inf'), "models": set()})
    
    # Process each file individually
    for file in files:
        parts = file.replace("comparison_", "").replace(".jsonl", "").split("_by_")
        # Ensure file follows the naming convention: target_model_by_analyse_model
        if len(parts) != 2:
            continue
        target_model, analyse_model = parts[0], parts[1]
        # Skip if analysis model is the same as target model
        if analyse_model == target_model:
            continue
        
        file_path = os.path.join(input_folder, file)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                entry = json.loads(line)
                entry_id = entry["id"]
                score = entry.get("score")
                if isinstance(score, (int, float)):
                    # Update if a new best score is found
                    if score > global_best_scores[entry_id]["score"]:
                        global_best_scores[entry_id]["score"] = score
                        global_best_scores[entry_id]["models"] = {analyse_model}
                    # If equal, add the analysis model to the set (ensuring uniqueness)
                    elif score == global_best_scores[entry_id]["score"]:
                        global_best_scores[entry_id]["models"].add(analyse_model)
    
    # Write the aggregated best scores to a single JSONL file
    output_file = os.path.join(output_folder, "BestModel.jsonl")
    with open(output_file, "w", encoding="utf-8") as out_f:
        for entry_id, data in global_best_scores.items():
            out_f.write(json.dumps({
                "id": entry_id,
                "score": data["score"],
                "best_models": ",".join(sorted(data["models"]))
            }) + "\n")
    
    print(f"Saved global best scores to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find global best scores from comparison JSONL files.")
    parser.add_argument("--input_folder", required=True, help="Folder containing comparison JSONL files.")
    parser.add_argument("--output_folder", required=True, help="Folder to store the global best score JSONL file.")
    
    args = parser.parse_args()
    
    os.makedirs(args.output_folder, exist_ok=True)
    process_files(args.input_folder, args.output_folder)
