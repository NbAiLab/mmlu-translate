# MMLU Translation Tools

This repository provides tools for translating the Massive Multitask Language Understanding (MMLU) dataset from English to Norwegian, along with evaluation scripts.

The final dataset itself is available [on HuggingFace](https://huggingface.co/datasets/NbAiLab/nb-global-mmlu)

## Contents

- **[Research Protocol](research_protocol.md):** Details the translation process, quality scoring, and evaluation strategy.
- **[Translation Quality Evaluation](translation_quality_evaluation.md):** Evaluation of translation quality.
- **Translation Scripts:** Tools to accurately translate MMLU questions while preserving structure and meaning.
- **Evaluation Tools:** Built upon [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness) to assess translation quality and model performance on both Norwegian and English datasets.

## Overview

The MMLU dataset includes over 14,000 multiple-choice questions across 57 subjects. High-quality translations ensure that the original difficulty and context are maintained for Norwegian audiences.

## Usage
This repo is designed to be used with the [lm-evaluation-harness](https://github.com/EleutherAI/lm-evaluation-harness). 
Example usage:
```
git clone --depth 1 https://github.com/EleutherAI/lm-evaluation-harness
cd lm-evaluation-harness
pip install -e .

cd ..
git clone https://github.com/NbAiLab/mmlu-translate
cd mmlu-translate

lm_eval \                                          
  --model hf \
  --model_args pretrained=<org>/<model> \
  --tasks global_mmlu_full_nb \
  --include_path ./mmlu-translate/tasks \
  --output results/mmlu-translate/0-shot/<org>/<model> \
  --log_samples \
  --show_config \
  --write_out \
  --batch_size auto \
  --num_fewshot 0
```

## License
This project is licensed under the MIT License.

