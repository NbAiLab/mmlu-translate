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
