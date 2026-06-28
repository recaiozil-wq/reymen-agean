---
name: ecc_pytorch-patterns_references_bad-no-shape-tracking
description: "Bad: No shape tracking"
title: "Ecc Pytorch Patterns References Bad No Shape Tracking"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: No shape tracking |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: No shape tracking
def forward(self, x):
    x = self.conv1(x)
    x = self.pool(x)
    x = x.view(x.size(0), -1)  # What size is this?
    return self.fc(x)           # Will this even work?
```
