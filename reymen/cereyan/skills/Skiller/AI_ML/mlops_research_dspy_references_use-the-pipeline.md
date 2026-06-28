---
name: mlops_research_dspy_references_use-the-pipeline
description: Use the pipeline
title: "Mlops Research Dspy References Use The Pipeline"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Use the pipeline |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Use the pipeline
qa_system = MultiHopQA()
result = qa_system(question="Who wrote the book that inspired the movie Blade Runner?")
```

#### RAG System with Optimization

```python
import dspy
from dspy.retrieve.chromadb_rm import ChromadbRM
