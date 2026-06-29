---
name: mlops_evaluation_weights-and-biases_references_enable-offline-mode
description: Enable offline mode
title: "Mlops Evaluation Weights And Biases References Enable Offline Mode"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Enable offline mode |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Enable offline mode
os.environ["WANDB_MODE"] = "offline"

wandb.init(project="my-project")
