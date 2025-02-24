#!/usr/bin/env python3
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
    
    # ===== Begin evaluator calibration and weighted aggregation section =====
    # Perform two passes: first, to calibrate evaluator biases using only valid scores (1-5)
    # and compute weights, and second, to compute weighted averages for each (entry_id, target_model) pair.
    
    # Dictionaries for evaluator calibration and storing evaluations.
    evaluator_scores = defaultdict(list)  # key: analysis_model, value: list of valid scores
    evaluations = []  # list of tuples: (entry_id, target_model, score, analysis_model)
    
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
                # Collect evaluator scores for calibration
                evaluator_scores[analysis_model].append(score)
                # Store the evaluation record
                evaluations.append((entry_id, target_model, score, analysis_model))
    
    # Compute the global mean of all valid scores from evaluators
    all_valid_scores = []
    for scores in evaluator_scores.values():
        all_valid_scores.extend(scores)
    
    if all_valid_scores:
        global_mean = sum(all_valid_scores) / len(all_valid_scores)
    else:
        global_mean = 0.0
    
    # Calculate weights for each evaluator based on their average score
    evaluator_weights = {}
    evaluator_means = {}
    for evaluator, scores in evaluator_scores.items():
        evaluator_mean = sum(scores) / len(scores)
        evaluator_means[evaluator] = evaluator_mean
        evaluator_weights[evaluator] = global_mean / evaluator_mean if evaluator_mean != 0 else 1.0

    # Print the evaluator weights as a Markdown table with three-digit accuracy,
    # including the entire formula on a single line with the final answer in bold.
    # The printed formula is:
    # $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{GLOBAL_MEAN}{EVALUATOR_MEAN} = \mathbf{FINAL_WEIGHT}$$
    print("| Evaluator Model             | Formula                                                              |")
    print("|-----------------------------|----------------------------------------------------------------------|")
    for evaluator, weight in sorted(evaluator_weights.items()):
        eval_mean = evaluator_means[evaluator]
        formula = f"$$w = \\frac{{\\text{{Global Mean}}}}{{\\text{{Evaluator Mean}}}} = \\frac{{{global_mean:6.3f}}}{{{eval_mean:6.3f}}} = \\mathbf{{{weight:6.3f}}}$$"
        print(f"| {evaluator:<27} | {formula:<70} |")
    
    # Compute weighted averages for each (entry_id, target_model)
    weighted_scores_by_entry_target = defaultdict(lambda: {"weighted_sum": 0.0, "total_weight": 0.0})
    for entry_id, target_model, score, analysis_model in evaluations:
        weight = evaluator_weights.get(analysis_model, 1.0)
        weighted_scores_by_entry_target[(entry_id, target_model)]["weighted_sum"] += score * weight
        weighted_scores_by_entry_target[(entry_id, target_model)]["total_weight"] += weight
    
    weighted_avg_by_entry_target = {}
    for (entry_id, target_model), data in weighted_scores_by_entry_target.items():
        if data["total_weight"] > 0:
            weighted_avg_by_entry_target[(entry_id, target_model)] = data["weighted_sum"] / data["total_weight"]
    # ===== End evaluator calibration and weighted aggregation section =====
    
    # Second level: For each entry, select the target model(s) with the highest weighted average score
    global_best = defaultdict(lambda: {"score": float('-inf'), "models": set()})
    for (entry_id, target_model), mean_score in weighted_avg_by_entry_target.items():
        if mean_score > global_best[entry_id]["score"]:
            global_best[entry_id]["score"] = mean_score
            global_best[entry_id]["models"] = {target_model}
        elif mean_score == global_best[entry_id]["score"]:
            global_best[entry_id]["models"].add(target_model)
    
    # Write the aggregated best weighted average scores to the specified output file.
    with open(output_file, "w", encoding="utf-8") as out_f:
        for entry_id, data in global_best.items():
            out_f.write(json.dumps({
                "id": entry_id,
                "score": data["score"],
                "best_models": ",".join(sorted(data["models"]))
            }) + "\n")
    
    print(f"Saved global best weighted scores to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find global best weighted mean scores from comparison JSONL files.")
    parser.add_argument("--input_folder", required=True, help="Folder containing comparison JSONL files.")
    parser.add_argument("--output_file", required=True, help="File to store the global best weighted mean score JSONL output.")
    parser.add_argument("--exclude_reasoning", action="store_true",
                        help="If set, exclude any file with 'R1' as part of the model name.")
    parser.add_argument("--exclude_smallmodels", action="store_true",
                        help="If set, exclude files whose target or analysis model is one of the following: "
                             "Llama-3.3-70B-Instruct-Turbo, Meta-Llama-3.1-70B-Instruct, Qwen2.5-72B-Instruct, "
                             "Mistral-Small-24B-Instruct-2501.")
    
    args = parser.parse_args()
    
    process_files(args.input_folder, args.output_file, args.exclude_reasoning, args.exclude_smallmodels)
