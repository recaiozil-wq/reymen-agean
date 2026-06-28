---
name: software-development_self-improvement-loop_references_root-level-shim-pattern
description: Root-Level Shim Pattern — Session 2026-06-21
title: "Software Development Self Improvement Loop References Root Level Shim Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Root-Level Shim Pattern — Session 2026-06-21 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Root-Level Shim Pattern — Session 2026-06-21

## Problem
Hermes internal modules exist in subdirectories (`agent/`, `tools/`), but tests import them from root.

## Solution
Create one-liner shim at project root:
```python
# auxiliary_client.py
from agent.auxiliary_client import *  # noqa: F401, F403
```

For deeply nested modules, use sys.path:
```python
import sys, os
_dir = os.path.join(os.path.dirname(__file__), 'desktop', 'dist', 'win-unpacked', 'resources')
if _dir not in sys.path:
    sys.path.insert(0, _dir)
from web_ui import *
```

## Unix-Only Modules on Windows
In `conftest.py`:
```python
import types
for mod in ('termios', 'curses', 'pwd'):
    if mod not in sys.modules:
        try: __import__(mod)
        except ImportError: sys.modules[mod] = types.ModuleType(mod)
```

## Creating Modules From Scratch
When tests import a nonexistent ReYMeN module:
1. Read test imports to find required exports
2. Create minimal implementation at project root
3. Verify: `python -c "from module import symbol"`

Example: `anayasa_denetcisi.py` (content moderation), `voice_mixer.py` (PCM audio)
