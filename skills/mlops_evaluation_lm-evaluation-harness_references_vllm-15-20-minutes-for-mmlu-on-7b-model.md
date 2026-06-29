---
name: mlops_evaluation_lm-evaluation-harness_references_vllm-15-20-minutes-for-mmlu-on-7b-model
description: "vLLM: ~15-20 minutes for MMLU on 7B model"
title: "Mlops Evaluation Lm Evaluation Harness References Vllm 15 20 Minutes For Mmlu On 7B Model"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | vLLM: ~15-20 minutes for MMLU on 7B model |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# vLLM: ~15-20 minutes for MMLU on 7B model
lm_eval --model vllm \
  --model_args pretrained=meta-llama/Llama-2-7b-hf,tensor_parallel_size=2 \
  --tasks mmlu \
  --batch_size auto
```
