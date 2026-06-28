---
name: mlops_evaluation_weights-and-biases_references_save-model
description: Save model
title: "Mlops Evaluation Weights And Biases References Save Model"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Save model |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Save model
torch.save(model.state_dict(), "model.pth")
wandb.save("model.pth")  # Upload to W&B

wandb.finish()
```
