---
name: mlops_research_dspy_references_create-evaluator
description: Create evaluator
title: "Mlops Research Dspy References Create Evaluator"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Create evaluator |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Create evaluator
evaluator = Evaluate(
    devset=testset,
    metric=exact_match,
    num_threads=4,
    display_progress=True
)
