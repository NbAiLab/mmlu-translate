# Translation Run
Below is all the commands used in the main translation run. 

Based on the experiments on the dev-set, and the cost calculations available in [this document](translation_experiment.md) it was decided to have these main comparisons:

## Experiments
| ExpID | Model                                                    | Description                                   | Status                     | 
|-------|----------------------------------------------------------|-----------------------------------------------|---------------------------------|
| 1     | DeepSeek R1                                              | Single model                                  | Done                            |
| 2     | DeepSeek V3                                              | Single model                                  | Done                            |
| 3     | Llama 405B                                               | Single model                                  | Done                            |
| 4     | Llama 70B                                                | Single model                                  | Done                            |
| 5     | DeepSeek V3 - Llama 405B - Llama 70B                     | Best out of 3 models                          | Done                            |
| 6     | DeepSeek R1 - DeepSeek V3 - Llama 405B - Llama 70B       | Best out of 4 models                          | Done                            |
| 7     | Alexandra Institute                                      | External dataset                              | -                               |
| 8     | DeepSeek R1 == 5                                         | Single model (9397 lines)                     | -                               |
| 9     | English where DeepSeek R1 == 5                           | Single model (9397 lines)                     | -                               |
| 10     | DeepSeek R1 blindly selects best translation            | Single model                                  | -                               |


## Translating the Models
```bash
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-R1.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-R1
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_DeepSeek-V3.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-V3
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Meta-Llama-3.1-405B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-405B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_test_en.jsonl --output_file mmlu-no/test_Llama-3.3-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct
```

```bash
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file mmlu-no/dev_DeepSeek-R1.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-R1
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file mmlu-no/dev_DeepSeek-V3.jsonl --template_file templates/bokmal_template.txt --model deepseek-ai/DeepSeek-V3
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file mmlu-no/dev_Meta-Llama-3.1-405B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Meta-Llama-3.1-405B-Instruct
python mmlu_translate_deepinfra.py --input_file data/Global-MMLU_dev_en.jsonl --output_file mmlu-no/dev_Llama-3.3-70B-Instruct.jsonl --template_file templates/bokmal_template.txt --model meta-llama/Llama-3.3-70B-Instruct
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

```bash
cp mmlu-no/dev_DeepSeek-R1.jsonl mmlu-no-best/n1_dev.jsonl
cp mmlu-no/dev_DeepSeek-V3.jsonl mmlu-no-best/n2_dev.jsonl
cp mmlu-no/dev_Meta-Llama-3.1-405B-Instruct.jsonl  mmlu-no-best/n3_dev.jsonl
cp mmlu-no/dev_Llama-3.3-70B-Instruct.jsonl mmlu-no-best/n4_dev.jsonl
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

python mmlu_find_best_scores.py --input_folder mmlu-no-comparison-dev/ --output_file mmlu-no-best/n5_dev.jsonl --exclude_reasoning --exclude_smallmodels
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

python mmlu_find_best_scores.py --input_folder mmlu-no-comparison-dev/ --output_file mmlu-no-best/n6_dev.jsonl --exclude_smallmodels

```

In the end, clean this up and copy to mmlu-no-best-clean:
```bash
for f in mmlu-no-best/*.jsonl; do jq -c '{sample_id, subject, subject_category, question, option_a, option_b, option_c, option_d, answer, required_knowledge, time_sensitive, reference, culture, region, country, cultural_sensitivity_label, is_annotated}' "$f" > mmlu-no-best-clean/"$(basename "$f")"; done
```

### Alexandria Data
These data has another format, and needs special threatment. First concatenate into a single file:

```bash
cat test.jsonl train.jsonl val.jsonl > all.jsonl
```
For the dev-set here, we will just borrow the one from R1. This is just for prompting.

```bash
cp mmlu-no-best-clean/n1_dev.jsonl mmlu-no-best-clean/n7_dev.jsonl
```

### ExpID 8++
In experiment #8 we extract only the scores where the model is certain that the score is 5 (N=9397).

```bash
jq -c 'select(.score == 5)' n1.jsonl > n8.jsonl
```

To make sure we do not only select the simple tasks here, we also check the corresponding lines from the English dataset. 

```bash
while IFS= read -r n1_line && IFS= read -r en_line <&3; do echo "$n1_line" | jq -e 'select(.score==5)' > /dev/null && echo "$en_line"; done < n1.jsonl 3< en.jsonl > n9.jsonl
```



## Generating dataset
Run the following command to convert the dataset to Global-MMLU HuggingFace format.
```bash
python make_dataset.py --input_files mmlu-no-best-clean/* --output_folder path_to_dataset/
```

## Results
Results when running with lm-evaluation-harness:
| Model                            | Subset | Score  |
|----------------------------------|--------|--------|
| meta-llama/Llama-3.1-8B-Instruct | en     | 66.02% |
| meta-llama/Llama-3.1-8B-Instruct | n1     | 52.14% |
| meta-llama/Llama-3.1-8B-Instruct | n2     | 51.96% |
| meta-llama/Llama-3.1-8B-Instruct | n3     | 51.30% |
| meta-llama/Llama-3.1-8B-Instruct | n4     | 51.22% |
| meta-llama/Llama-3.1-8B-Instruct | n5     | 51.82% |
| meta-llama/Llama-3.1-8B-Instruct | n6     | 51.94% |
| meta-llama/Llama-3.1-8B-Instruct | n7     | 50.62% |
| meta-llama/Llama-3.1-8B-Instruct | n8     | 52.77% |
| meta-llama/Llama-3.1-8B-Instruct | n9     | 65.96% |
| meta-llama/Llama-3.1-8B-Instruct | n10    | 52.16% |
