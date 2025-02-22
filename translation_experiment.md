# Translation Experiment

```bash
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_Llama-3.3-70B-Instruct-Turbo.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct-Turbo
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_DeepSeek-R1.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-R1
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_DeepSeek-V3.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-V3
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_Llama-3.3-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_Meta-Llama-3.1-405B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-405B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_Meta-Llama-3.1-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-70B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_Qwen2.5-72B-Instruct.jsonl --template_file templates/bokmal_template.txt --model Qwen/Qwen2.5-72B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file experiment/dev_Mistral-Small-24B-Instruct-2501.jsonl --template_file templates/bokmal_template.txt --model mistralai/Mistral-Small-24B-Instruct-2501
```

# Download the alexndria dataset. Then adapt it
```bash
jq 'with_entries(if .key == "instruction" then .key = "question" else . end)' -c dev_alexandria.jsonl > temp.jsonl && mv temp.jsonl dev_alexndria.jsonl
jq 'with_entries(if .key == "instruction" then .key = "question" else . end)' -c en.jsonl > temp.jsonl && mv temp.jsonl en.jsonl
jq 'with_entries(if .key == "id" then .key = "sample_id" else . end)' -c dev_alexandria.jsonl > temp.jsonl && mv temp.jsonl dev_alexandria.jsonl
jq 'with_entries(if .key == "id" then .key = "sample_id" else . end)' -c en.jsonl > temp.jsonl && mv temp.jsonl en.jsonl
```

# Compare models
```bash
bash run_comparison.sh
bash run_alexandria_comparison.sh
```

# Find Best Scores
```bash
python mmlu_find_best_scores.py --input_folder experiment_compare/ --output_file experiment_compare/comparison_BestModelWithoutSmall_by_BestModelWithoutSmall.jsonl --exclude_reasoning --exclude_smallmodels
python mmlu_find_best_scores.py --input_folder experiment_compare/ --output_file experiment_compare/comparison_BestModelWithoutReasoning_by_BestModelWithoutReasoning.jsonl --exclude_reasoning
python mmlu_find_best_scores.py --input_folder experiment_compare/ --output_file experiment_compare/comparison_BestModel_by_BestModel.jsonl
```

# Create MarkDown
```bash
python mmlu_analyse_comparisons.py
```

# Cost Estimates - Translation
DeepSeek-R1 - 285 examples = $1.34182635 -> $65.913 for 14k
DeepSeek-V3 - 285 examples = $0.30226221 -> $14.848 for 14k
Llama_3.1-405B - 285 examples = $0.43798800 -> $21.515 for 14k
Llama_3.3-70B - 285 examples = $0.14283057 -> $7.016 for 14k

# Price - Comparison x N
DeepSeek-R1 - 285 examples = $0.91000590 -> $44.702 for 14k
DeepSeek-V3 - 285 examples - $0.08400600 -> $4.127
Llama_3.1-405B - 285 examples = $0.17398000 -> $8.564 for 14k
Llama_3.3-70B - 285 examples = $0.05175618 -> $2.542 for 14k

| Model            | Translation | Comparison |
|-----------------|------------|------------|
| DeepSeek R1     | $66        | $44        |
| DeepSeek V3     | $15        | $4         |
| Llama 3.1 405B  | $21        | $9         |
| Llama 3.3 70B   | $7         | $3         |

| Model                                      | Calculation                                                    | Cost  | Comment      |
|--------------------------------------------|----------------------------------------------------------------|-------|--------------|
| R1                                         | -                                                              | $66   |OK            |
| V3-405B-70B-comparison                     | ($15 + $21 + $7) + (3 × $4 + 3 × $9 + 3 × $3)                  | $91   |OK            |
| R1-V3-405B-70B-comparison                  | ($66 + $15 + $21 + $7) + (4 × $44 + 4 × $4 + 4 × $9 + 4 × $3)  | $349  |Too expensive |
| V3                                         | $15 but included above                                         | $0    |OK            |
| Alexandra Institute external               | external                                                       | $0    |OK            |




