import os
import json
import argparse
from collections import defaultdict

def process_files(input_folder, output_file, exclude_reasoning=False, exclude_smallmodels=False):
    # List all relevant files from input_folder.
    # Exclude files with "Alexandria", "BestModel", and optionally "R1" in the filename.
    files = [
        f for f in os.listdir(input_folder)
        if f.startswith("comparison_") and f.endswith(".jsonl")
        and "Alexandria" not in f
        and "BestModel" not in f
        and (not exclude_reasoning or "R1" not in f)
    ]
    
    # Debug: print total number of files processed
    print(f"[DEBUG] Total files processed: {len(files)}")
    
    # Define the set of small models to exclude.
    excluded_models = {
        "Llama-3.3-70B-Instruct-Turbo",
        "Meta-Llama-3.1-70B-Instruct",
        "Qwen2.5-72B-Instruct",
        "Mistral-Small-24B-Instruct-2501"
    }
    
    # Accumulate valid scores per (entry_id, target_model)
    scores_by_entry_target = defaultdict(list)
    
    for file in files:
        # Parse filename: expecting format "comparison_<target_model>_by_<analysis_model>.jsonl"
        parts = file.replace("comparison_", "").replace(".jsonl", "").split("_by_")
        if len(parts) != 2:
            continue
        target_model, analysis_model = parts[0], parts[1]
        # Skip self-evaluation: if analysis_model is exactly equal to target_model
        if analysis_model == target_model:
            continue
        
        # If the flag is set, skip files where either model is in the excluded list.
        if exclude_smallmodels and (target_model in excluded_models or analysis_model in excluded_models):
            continue
        
        file_path = os.path.join(input_folder, file)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                entry_id = entry.get("id")
                score = entry.get("score")
                # Only consider numeric scores between 1 and 5
                if not isinstance(score, (int, float)):
                    continue
                if score < 1 or score > 5:
                    continue
                # Accumulate score for the (entry_id, target_model)
                scores_by_entry_target[(entry_id, target_model)].append(score)
    
    # First level: Compute the mean for each (entry_id, target_model)
    avg_by_entry_target = {}
    for (entry_id, target_model), scores in scores_by_entry_target.items():
        if scores:
            mean_score = sum(scores) / len(scores)
            # Debug info commented out:
            # print(f"[DEBUG] Entry: {entry_id}, Target: {target_model}, Scores: {scores}, Mean: {mean_score}")
            avg_by_entry_target[(entry_id, target_model)] = mean_score
    
    # Second level: For each entry, select the target model(s) with the highest mean score
    global_best = defaultdict(lambda: {"score": float('-inf'), "models": set()})
    for (entry_id, target_model), mean_score in avg_by_entry_target.items():
        if mean_score > global_best[entry_id]["score"]:
            global_best[entry_id]["score"] = mean_score
            global_best[entry_id]["models"] = {target_model}
        elif mean_score == global_best[entry_id]["score"]:
            global_best[entry_id]["models"].add(target_model)
    
    # Write the aggregated best mean scores to the specified output file.
    with open(output_file, "w", encoding="utf-8") as out_f:
        for entry_id, data in global_best.items():
            out_f.write(json.dumps({
                "id": entry_id,
                "score": data["score"],
                "best_models": ",".join(sorted(data["models"]))
            }) + "\n")
    
    print(f"Saved global best scores to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find global best mean scores from comparison JSONL files.")
    parser.add_argument("--input_folder", required=True, help="Folder containing comparison JSONL files.")
    parser.add_argument("--output_file", required=True, help="File to store the global best mean score JSONL output.")
    parser.add_argument("--exclude_reasoning", action="store_true",
                        help="If set, exclude any file with 'R1' as part of the model name.")
    parser.add_argument("--exclude_smallmodels", action="store_true",
                        help="If set, exclude files whose target or analysis model is one of the following: "
                             "Llama-3.3-70B-Instruct-Turbo, Meta-Llama-3.1-70B-Instruct, Qwen2.5-72B-Instruct, "
                             "Mistral-Small-24B-Instruct-2501.")
    
    args = parser.parse_args()
    
    process_files(args.input_folder, args.output_file, args.exclude_reasoning, args.exclude_smallmodels)
