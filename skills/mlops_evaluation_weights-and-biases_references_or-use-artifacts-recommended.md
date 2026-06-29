---
name: mlops_evaluation_weights-and-biases_references_or-use-artifacts-recommended
description: Or use Artifacts (recommended)
title: "Mlops Evaluation Weights And Biases References Or Use Artifacts Recommended"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Or use Artifacts (recommended) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Or use Artifacts (recommended)
artifact = wandb.Artifact('model', type='model')
artifact.add_file('checkpoint.pth')
wandb.log_artifact(artifact)
```
