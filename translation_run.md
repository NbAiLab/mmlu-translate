# Translation Run
Below is all the commands used in the main translation run. 

Based on the experiments on the dev-set, and the cost calculations available in [this document](translation_experiment.md) it was decided to have these main comparisons:

## Experiment Cost
| ExpID | Model                                                    | Description                                   | Status/Cost                     | 
|-------|----------------------------------------------------------|-----------------------------------------------|---------------------------------|
| 1     | DeepSeek R1                                              | Single model                                  | Done                            |
| 2     | DeepSeek V3                                              | Single model                                  | Done                            |
| 3     | Llama 405B                                               | Single model                                  | Done                            |
| 4     | Llama 70B                                                | Single model                                  | Done                            |
| 5     | DeepSeek V3 - Llama 405B - Llama 70B                     | Best out of 3 models                          | Done                            |
| 6     | DeepSeek R1 - DeepSeek V3 - Llama 405B - Llama 70B       | Best out of 4 models                          | Running                         |
| 7     | Alexandra Institute                                      | External dataset                              | -                               |


## Translating the Models
```bash
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-R1.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-R1
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-V3.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-V3
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Meta-Llama-3.1-405B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-405B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Llama-3.3-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct
```

## Comparing the Models
We can run the comparison with the following command:

```bash
bash run_comparison.sh
```

The script will then run the following script and loop over all models and translations

```bash
models=("deepseek-ai/DeepSeek-V3" "meta-llama/Llama-3.3-70B-Instruct" "meta-llama/Meta-Llama-3.1-405B-Instruct" "deepseek-ai/DeepSeek-R1")
translated_files=("test_DeepSeek-R1.jsonl"  "test_DeepSeek-V3.jsonl"  "test_Llama-3.3-70B-Instruct.jsonl"  "test_Meta-Llama-3.1-405B-Instruct.jsonl")

for model in "${models[@]}"; do
    model_name=$(echo "$model" | sed 's|.*/||')  # Extract model name after last "/"
    for translated_file in "${translated_files[@]}"; do
        translated_model_name=$(echo "$translated_file" | sed 's/^dev_//' | sed 's/\.jsonl$//')
        output_file="mmlu-no-comparison/comparison_${translated_model_name}_by_${model_name}.jsonl"
        echo "Running comparison: Model=$model, Translated file=$translated_file"
        python mmlu_comparison_deepinfra.py --english_file data/Global-MMLU_test_en.jsonl --norwegian_file mmlu-no/${translated_file} --output_file ${output_file} --model ${model}
    done
done
```

## Selcting the Correct Entries
For the single model translations, the dataset is in reality already completed. However, for the datasets that needs evaluation it must go through another procedure.

Raw score aggregation was found to be susceptible to evaluator bias, where certain evaluator models systematically awarded higher scores than others. This bias can unfairly inflate the perceived performance of target models, particularly when low-quality models are assessed by overly positive evaluators. To mitigate this, we implement a weighted aggregation approach. Each evaluator’s score is adjusted by a weight calculated as the ratio of the global mean score to the evaluator’s mean score, computed from valid scores. This normalization ensures that out-of-range or erroneous evaluations do not skew the calibration, leading to a fairer and more accurate comparison of model performance.

The following weighted averages where calculated:




