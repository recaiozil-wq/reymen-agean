---
name: ecc_python-patterns_references_bad-o-n-due-to-string-immutability
description: "Bad: O(n²) due to string immutability"
title: "Ecc Python Patterns References Bad O N Due To String Immutability"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bad: O(n²) due to string immutability |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bad: O(n²) due to string immutability
result = ""
for item in items:
    result += str(item)
