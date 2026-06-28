---
name: software-development_python-debugpy_references_when-it-crashes-pdb-catches-it-and-you-re-in-the-frame-of-th
description: When it crashes, pdb catches it and you're in the frame of the exception
title: "Software Development Python Debugpy References When It Crashes Pdb Catches It And You Re In The Frame Of Th"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | When it crashes, pdb catches it and you're in the frame of the exception |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# When it crashes, pdb catches it and you're in the frame of the exception
```

Or set a global hook in a repl/jupyter:

```python
import sys
def excepthook(etype, value, tb):
    import pdb; pdb.post_mortem(tb)
sys.excepthook = excepthook
```
