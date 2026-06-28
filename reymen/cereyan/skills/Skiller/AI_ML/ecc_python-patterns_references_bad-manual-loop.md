---
name: ecc_python-patterns_references_bad-manual-loop
description: "Bad: Manual loop"
title: "Ecc Python Patterns References Bad Manual Loop"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Manual loop |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Manual loop
names = []
for user in users:
    if user.is_active:
        names.append(user.name)
