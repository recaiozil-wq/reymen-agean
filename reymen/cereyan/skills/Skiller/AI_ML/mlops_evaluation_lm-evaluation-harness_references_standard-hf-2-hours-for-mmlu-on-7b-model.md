---
name: mlops_evaluation_lm-evaluation-harness_references_standard-hf-2-hours-for-mmlu-on-7b-model
description: "Standard HF: ~2 hours for MMLU on 7B model"
title: "Mlops Evaluation Lm Evaluation Harness References Standard Hf 2 Hours For Mmlu On 7B Model"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Standard HF: ~2 hours for MMLU on 7B model |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Standard HF: ~2 hours for MMLU on 7B model
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu \
  --batch_size 8
