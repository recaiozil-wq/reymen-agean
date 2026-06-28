---
name: ecc_pytorch-patterns_references_bad-hardcoded-device
description: "Bad: Hardcoded device"
title: "Ecc Pytorch Patterns References Bad Hardcoded Device"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Hardcoded device |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Hardcoded device
model = MyModel().cuda()  # Crashes if no GPU
data = data.cuda()
```

### 2. Reproducibility First

Set all random seeds for reproducible results.

```python
