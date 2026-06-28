---
name: ecc_python-patterns_references_bad-mutable-default-arguments
description: "Bad: Mutable default arguments"
title: "Ecc Python Patterns References Bad Mutable Default Arguments"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: Mutable default arguments |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: Mutable default arguments
def append_to(item, items=[]):
    items.append(item)
    return items
