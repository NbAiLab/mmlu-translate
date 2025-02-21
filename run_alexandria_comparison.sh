#!/bin/bash

models=("deepseek-ai/DeepSeek-V3" "meta-llama/Llama-3.3-70B-Instruct" "meta-llama/Llama-3.3-70B-Instruct-Turbo" "meta-llama/Meta-Llama-3.1-405B-Instruct" "meta-llama/Meta-Llama-3.1-70B-Instruct" "Qwen/Qwen2.5-72B-Instruct" "mistralai/Mistral-Small-24B-Instruct-2501" "deepseek-ai/DeepSeek-R1")

translated_files=("dev_alexandria.jsonl")

for model in "${models[@]}"; do
    model_name=$(echo "$model" | sed 's|.*/||')  # Extract model name after last "/"
    for translated_file in "${translated_files[@]}"; do
        translated_model_name=$(echo "$translated_file" | sed 's/^dev_//' | sed 's/\.jsonl$//')
        output_file="experiment_compare/comparison_${translated_model_name}_by_${model_name}.jsonl"
        echo "Running comparison: Model=$model, Translated file=$translated_file"
        python mmlu_comparison_deepinfra.py --english_file alexandria_data/en.jsonl --norwegian_file alexandria_data/${translated_file} --output_file ${output_file} --model ${model}
    done
done
