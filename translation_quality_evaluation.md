# Translation Quality Evaluation
We did ask all the models to evaluate each others translations. This was done on the 285 lines dev-files.


## Some major points:
- Most models seem to have a positive self-image, evaluating their own results slightly better
- DeepSeek-R1 is by far the most critical model
- Mistral-Small-24B-Instruct-2501 and Qwen2.5-72B-Instruct is unsuited for translating English to Norwegian
- Maybe only DeepSeek-R1, DeepSeek-V3, Meta-Llama-3.1-405B-Instruct and Llama-3.3-70B-Instruct should be used
- The scores are suprisingly consistent. Everyone seems to agree what a bad translation looks like, even when the model itself is not able to translate at high quality
 

### Translation Quality Table
|                                 |   DeepSeek-R1 |   DeepSeek-V3 |   Llama-3.3-70B-Instruct |   Llama-3.3-70B-Instruct-Turbo |   Meta-Llama-3.1-405B-Instruct |   Meta-Llama-3.1-70B-Instruct |   Mistral-Small-24B-Instruct-2501 |   Qwen2.5-72B-Instruct |
|:--------------------------------|--------------:|--------------:|-------------------------:|-------------------------------:|-------------------------------:|------------------------------:|----------------------------------:|-----------------------:|
| Alexandria_Institute            |          4.12 |          4.34 |                     4.65 |                           4.66 |                           4.89 |                          4.82 |                              4.15 |                   4.25 |
| DeepSeek-R1                     |          **4.58** |          4.56 |                     4.75 |                           4.76 |                           4.96 |                          4.82 |                              4.25 |                   4.4  |
| DeepSeek-V3                     |          4.33 |         **4.46** |                     4.75 |                           4.74 |                           4.93 |                          4.84 |                              4.37 |                   4.4  |
| Llama-3.3-70B-Instruct          |          3.85 |          4.27 |                     **4.62** |                           4.65 |                           4.81 |                          4.74 |                              4.23 |                   4.29 |
| Llama-3.3-70B-Instruct-Turbo    |          3.8  |          4.2  |                     4.63 |                           **4.63** |                           4.8  |                          4.84 |                              4.18 |                   4.27 |
| Meta-Llama-3.1-405B-Instruct    |          4.22 |          4.43 |                     4.75 |                           4.75 |                           **4.94** |                          4.86 |                              4.39 |                   4.42 |
| Meta-Llama-3.1-70B-Instruct     |          3.88 |          4.32 |                     4.53 |                           4.54 |                           4.74 |                          **4.7**  |                              4.23 |                   4.32 |
| Mistral-Small-24B-Instruct-2501 |          2.94 |          3.36 |                     2.49 |                           2.49 |                           2.97 |                          3    |                              **3.31** |                   3.48 |
| Qwen2.5-72B-Instruct            |          3.06 |          3.69 |                     3.57 |                           3.59 |                           3.89 |                          3.97 |                              3.72 |                   **3.87** |


### Average Performance Translations (Excluding Self-Evaluation)
|                                 |   Average Translation Score |
|:--------------------------------|----------------------------:|
| DeepSeek-R1                     |                        4.64 |
| DeepSeek-V3                     |                        4.62 |
| Meta-Llama-3.1-405B-Instruct    |                        4.55 |
| Alexandria_Institute            |                        4.49 |
| Llama-3.3-70B-Instruct          |                        4.41 |
| Llama-3.3-70B-Instruct-Turbo    |                        4.39 |
| Meta-Llama-3.1-70B-Instruct     |                        4.37 |
| Qwen2.5-72B-Instruct            |                        3.64 |
| Mistral-Small-24B-Instruct-2501 |                        2.96 |


### Strictness in Evaluating Translations (Excluding Self-Evaluation)
|                                 |   Evaluation Strictness |
|:--------------------------------|------------------------:|
| DeepSeek-R1                     |                    3.78 |
| DeepSeek-V3                     |                    4.15 |
| Mistral-Small-24B-Instruct-2501 |                    4.19 |
| Qwen2.5-72B-Instruct            |                    4.23 |
| Llama-3.3-70B-Instruct          |                    4.26 |
| Llama-3.3-70B-Instruct-Turbo    |                    4.27 |
| Meta-Llama-3.1-70B-Instruct     |                    4.49 |
| Meta-Llama-3.1-405B-Instruct    |                    4.5  |
| Alexandria_Institute            |                  nan    |



