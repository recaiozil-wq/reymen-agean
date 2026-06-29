---
name: software-development_python-debugpy_references_recipe-4-post-mortem-on-any-exception
description: "Recipe 4: Post-mortem on any exception"
title: "Software Development Python Debugpy References Recipe 4 Post Mortem On Any Exception"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Recipe 4: Post-mortem on any exception |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Recipe 4: Post-mortem on any exception

```python
import pdb, sys
try:
    run_the_thing()
except Exception:
    pdb.post_mortem(sys.exc_info()[2])
```

Or wrap a whole script:

```bash
python -m pdb -c continue script.py
