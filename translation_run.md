# Translation Run
Below is all the commands used in the main translation run. 

Based on the experiments on the dev-set, and the cost calculations available in [this document](translations_experiments) it was decided to have these main comparisons:

## Experiment Cost
| ExpID | Model                                      | Description                                   |
|-------|--------------------------------------------|-----------------------------------------------|
| 1     | DeepSeek R1                                | Single model                                  |
| 2     | DeepSeek V3                                | Single model                                  |
| 3     | DeepSeek V3 - Llama 405B - Llama 70B       | Best out of 3 models                          |
| 4     | Alexandra Institute                        | External dataset                              |


## Translating the Models
```bash
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-R1.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-R1
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-V3.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-V3
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Llama-3.3-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Meta-Llama-3.1-405B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-405B-Instruct
```

## Comparing the Models
TBD


