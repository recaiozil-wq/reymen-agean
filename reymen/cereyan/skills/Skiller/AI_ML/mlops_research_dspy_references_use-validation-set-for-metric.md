---
name: mlops_research_dspy_references_use-validation-set-for-metric
description: Use validation set for metric
title: "Mlops Research Dspy References Use Validation Set For Metric"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Use validation set for metric |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Use validation set for metric
def metric(example, pred, trace=None):
    return example.answer in pred.answer
```

### 4. Save and Load Optimized Models

```python
