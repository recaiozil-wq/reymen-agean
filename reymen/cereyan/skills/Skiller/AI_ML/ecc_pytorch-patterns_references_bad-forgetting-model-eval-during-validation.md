---
name: ecc_pytorch-patterns_references_bad-forgetting-model-eval-during-validation
description: "Bad: Forgetting model.eval() during validation"
title: "Ecc Pytorch Patterns References Bad Forgetting Model Eval During Validation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Forgetting model.eval() during validation |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Forgetting model.eval() during validation
model.train()
with torch.no_grad():
    output = model(val_data)  # Dropout still active! BatchNorm uses batch stats!
