---
name: ecc_pytorch-patterns_references_good-move-model-once-before-the-loop
description: "Good: Move model once before the loop"
title: "Ecc Pytorch Patterns References Good Move Model Once Before The Loop"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Good: Move model once before the loop |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Good: Move model once before the loop
model = model.to(device)
for data, target in dataloader:
    data, target = data.to(device), target.to(device)
