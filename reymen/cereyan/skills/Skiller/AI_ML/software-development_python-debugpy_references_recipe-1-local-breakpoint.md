---
name: software-development_python-debugpy_references_recipe-1-local-breakpoint
description: "Recipe 1: Local breakpoint"
title: "Software Development Python Debugpy References Recipe 1 Local Breakpoint"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Recipe 1: Local breakpoint |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Recipe 1: Local breakpoint

Easiest. Edit the file:

```python
def compute(x, y):
    result = some_helper(x)
    breakpoint()           # <-- drops into pdb here
    return result + y
```

Run the code normally. You land at the `breakpoint()` line with full access to locals.

**Don't forget to remove `breakpoint()` before committing.** Use `git diff` or a pre-commit grep:
```bash
rg -n 'breakpoint\(\)' --type py
```
