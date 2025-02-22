# Translation Run
Below is all the commands used in the main translation run. 

Based on the experiments on the dev-set, and the cost calculations available in [this document](translations_experiments) it was decided to have these main comparisons:

## Experiment Cost
| ExpID | Model                                      | Description                                   | Status/Cost                     | 
|-------|--------------------------------------------|-----------------------------------------------|---------------------------------|
| 1     | DeepSeek R1                                | Single model                                  | Running                         |
| 2     | DeepSeek V3                                | Single model                                  | Running                         |
| 3     | Llama 405B                                 | Single model                                  | Running                         |
| 4     | Llama 70B                                  | Single model                                  | Done. Cost $7.149               |
| 5     | DeepSeek V3 - Llama 405B - Llama 70B       | Best out of 3 models                          | TBD                             |
| 6     | Alexandra Institute                        | External dataset                              | -                               |


## Translating the Models
```bash
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-R1.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-R1
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-V3.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-V3
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Meta-Llama-3.1-405B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-405B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Llama-3.3-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct
```

## Comparing the Models
TBD


