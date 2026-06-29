---
name: mlops_lm-evaluation-harness_references_in-training-loop
description: In training loop
title: "Mlops Lm Evaluation Harness References In Training Loop"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | In training loop |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# In training loop
if step % eval_interval == 0:
    model.save_pretrained(f"checkpoints/step-{step}")
