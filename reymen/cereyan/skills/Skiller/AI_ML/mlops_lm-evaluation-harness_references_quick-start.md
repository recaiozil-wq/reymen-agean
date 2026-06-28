---
name: mlops_lm-evaluation-harness_references_quick-start
description: Quick start
title: "Mlops Lm Evaluation Harness References Quick Start"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Quick start |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Quick start

lm-evaluation-harness evaluates LLMs across 60+ academic benchmarks using standardized prompts and metrics.

**Installation**:
```bash
pip install lm-eval
```

**Evaluate any HuggingFace model**:
```bash
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag \
  --device cuda:0 \
  --batch_size 8
```

**View available tasks**:
```bash
lm_eval --tasks list
```
