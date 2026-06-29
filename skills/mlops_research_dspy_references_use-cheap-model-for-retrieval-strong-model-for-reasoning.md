---
name: mlops_research_dspy_references_use-cheap-model-for-retrieval-strong-model-for-reasoning
description: "Use cheap model for retrieval, strong model for reasoning"
title: "Mlops Research Dspy References Use Cheap Model For Retrieval Strong Model For Reasoning"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Use cheap model for retrieval, strong model for reasoning |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Use cheap model for retrieval, strong model for reasoning
with dspy.settings.context(lm=cheap_lm):
    context = retriever(question)

with dspy.settings.context(lm=strong_lm):
    answer = generator(context=context, question=question)
```
