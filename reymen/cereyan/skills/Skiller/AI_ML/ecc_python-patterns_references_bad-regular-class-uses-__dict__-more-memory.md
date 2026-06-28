---
name: ecc_python-patterns_references_bad-regular-class-uses-__dict__-more-memory
description: "Bad: Regular class uses __dict__ (more memory)"
title: "Ecc Python Patterns References Bad Regular Class Uses   Dict   More Memory"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Regular class uses __dict__ (more memory) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Regular class uses __dict__ (more memory)
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
