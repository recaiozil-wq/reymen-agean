---
name: ecc_pytorch-patterns_references_bad-moving-data-to-gpu-inside-the-training-loop-repeatedly
description: "Bad: Moving data to GPU inside the training loop repeatedly"
title: "Ecc Pytorch Patterns References Bad Moving Data To Gpu Inside The Training Loop Repeatedly"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Moving data to GPU inside the training loop repeatedly |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Moving data to GPU inside the training loop repeatedly
for data, target in dataloader:
    model = model.cuda()  # Moves model EVERY iteration!
