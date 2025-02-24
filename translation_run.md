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
| 6     | DeepSeek R1 - DeepSeek V3 - Llama 405B - Llama 70B       | Best out of 4 models                          | Done                            |
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
For the single model translations, the dataset is in reality already completed. 

```bash
cp mmlu-no/test_DeepSeek-R1.jsonl mmlu-no-best/n1.jsonl
cp mmlu-no/test_DeepSeek-V3.jsonl mmlu-no-best/n2.jsonl
cp mmlu-no/test_Meta-Llama-3.1-405B-Instruct.jsonl  mmlu-no-best/n3.jsonl
cp mmlu-no/test_Llama-3.3-70B-Instruct.jsonl mmlu-no-best/n4.jsonl
```

However, for the datasets that needs evaluation it must go through another procedure.

Raw score aggregation was found to be susceptible to evaluator bias, where certain evaluator models systematically awarded higher scores than others. This bias can unfairly inflate the perceived performance of target models, particularly when low-quality models are assessed by overly positive evaluators. To mitigate this, we implement a weighted aggregation approach. Each evaluator’s score is adjusted by a weight calculated as the ratio of the global mean score to the evaluator’s mean score, computed from valid scores. This normalization ensures that out-of-range or erroneous evaluations do not skew the calibration, leading to a fairer and more accurate comparison of model performance.

The following weighted ratios for expID=5 where calculated:
| Evaluator Model             | Weight Calculation                                                              |
|-----------------------------|----------------------------------------------------------------------|
| DeepSeek-V3                 | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.553}{ 4.347} = \mathbf{ 1.048}$$ |
| Llama-3.3-70B-Instruct      | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.553}{ 4.635} = \mathbf{ 0.982}$$ |
| Meta-Llama-3.1-405B-Instruct | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.553}{ 4.867} = \mathbf{ 0.936}$$ |

Run the following command to create this dataset:
```bash
python mmlu_find_best_scores.py --input_folder mmlu-no-comparison/ --output_file mmlu-no-best/n5.jsonl --exclude_reasoning --exclude_smallmodels
```



The following weighted tarios for expID=6 where calculated:
| Evaluator Model             | Weight Calculation                                                   |
|-----------------------------|----------------------------------------------------------------------|
| DeepSeek-R1                 | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.470}{ 4.206} = \mathbf{ 1.063}$$ |
| DeepSeek-V3                 | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.470}{ 4.382} = \mathbf{ 1.020}$$ |
| Llama-3.3-70B-Instruct      | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.470}{ 4.659} = \mathbf{ 0.960}$$ |
| Meta-Llama-3.1-405B-Instruct | $$w = \frac{\text{Global Mean}}{\text{Evaluator Mean}} = \frac{ 4.470}{ 4.883} = \mathbf{ 0.915}$$ |

Run the following command to create this dataset:

```bash
python mmlu_find_best_scores.py --input_folder mmlu-no-comparison/ --output_file mmlu-no-best/n6.jsonl --exclude_smallmodels
```

In the end, clean this up and copy to mmlu-no-best-clean:
```bash
for f in mmlu-no-best/*.jsonl; do jq -c '{sample_id, subject, subject_category, question, option_a, option_b, option_c, option_d, answer, required_knowledge, time_sensitive, reference, culture, region, country, cultural_sensitivity_label, is_annotated}' "$f" > mmlu-no-best-clean/"$(basename "$f")"; done
```

## Generating dataset
Run the following command to convert the dataset to Global-MMLU HuggingFace format.
```bash
python make_dataset.py --input_files mmlu-no-best-clean/* --output_folder path_to_dataset/
```
