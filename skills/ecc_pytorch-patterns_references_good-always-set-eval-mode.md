---
name: ecc_pytorch-patterns_references_good-always-set-eval-mode
description: "Good: Always set eval mode"
title: "Ecc Pytorch Patterns References Good Always Set Eval Mode"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Good: Always set eval mode |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Good: Always set eval mode
model.eval()
with torch.no_grad():
    output = model(val_data)
