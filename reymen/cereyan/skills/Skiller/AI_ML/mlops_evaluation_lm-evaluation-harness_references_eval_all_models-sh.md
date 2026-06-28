---
name: mlops_evaluation_lm-evaluation-harness_references_eval_all_models-sh
description: eval_all_models.sh
title: "Mlops Evaluation Lm Evaluation Harness References Eval All Models Sh"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | eval_all_models.sh |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# eval_all_models.sh

TASKS="mmlu,gsm8k,hellaswag,truthfulqa"

while read model; do
    echo "Evaluating $model"
