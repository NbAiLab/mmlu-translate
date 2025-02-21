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

# Price
R1 - 285 examples = $1.34182635

# Download the alexndria dataset. Then adapt it
```bash
jq 'with_entries(if .key == "instruction" then .key = "question" else . end)' -c dev_alexandria.jsonl > temp.jsonl && mv temp.jsonl dev_alexndria.jsonl
jq 'with_entries(if .key == "instruction" then .key = "question" else . end)' -c en.jsonl > temp.jsonl && mv temp.jsonl en.jsonl
jq 'with_entries(if .key == "id" then .key = "sample_id" else . end)' -c dev_alexandria.jsonl > temp.jsonl && mv temp.jsonl dev_alexandria.jsonl
jq 'with_entries(if .key == "id" then .key = "sample_id" else . end)' -c en.jsonl > temp.jsonl && mv temp.jsonl en.jsonl
```

# Compare models
bash run_comparison.sh
bash run_alexandria_comparison.sh

# Find Best Scores
python mmlu_find_best_scores.py --input_folder experiment_compare/ --output_file experiment_compare/comparison_BestModelWithoutSmall_by_BestModelWithoutSmall.jsonl --exclude_reasoning --exclude_smallmodels
python mmlu_find_best_scores.py --input_folder experiment_compare/ --output_file experiment_compare/comparison_BestModelWithoutReasoning_by_BestModelWithoutReasoning.jsonl --exclude_reasoning
python mmlu_find_best_scores.py --input_folder experiment_compare/ --output_file experiment_compare/comparison_BestModel_by_BestModel.jsonl

# Create MarkDown
python mmlu_analyse_comparisons.py
