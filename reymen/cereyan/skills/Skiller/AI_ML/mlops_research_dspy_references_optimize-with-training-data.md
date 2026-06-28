---
name: mlops_research_dspy_references_optimize-with-training-data
description: Optimize with training data
title: "Mlops Research Dspy References Optimize With Training Data"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Optimize with training data |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Optimize with training data
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(metric=validate_answer)
optimized_rag = optimizer.compile(rag, trainset=trainset)
```
