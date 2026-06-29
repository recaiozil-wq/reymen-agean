---
name: ecc_pytorch-patterns_references_bad-slow-defaults
description: "Bad: Slow defaults"
title: "Ecc Pytorch Patterns References Bad Slow Defaults"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Slow defaults |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Slow defaults
dataloader = DataLoader(dataset, batch_size=32)  # num_workers=0, no pin_memory
```

### Custom Collate for Variable-Length Data

```python
