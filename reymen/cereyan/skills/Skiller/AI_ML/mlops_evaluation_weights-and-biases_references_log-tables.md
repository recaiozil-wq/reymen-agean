---
name: mlops_evaluation_weights-and-biases_references_log-tables
description: Log tables
title: "Mlops Evaluation Weights And Biases References Log Tables"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Log tables |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Log tables
table = wandb.Table(columns=["id", "prediction", "ground_truth"])
wandb.log({"predictions": table})
```

### 4. Model Checkpointing

```python
import torch
import wandb
