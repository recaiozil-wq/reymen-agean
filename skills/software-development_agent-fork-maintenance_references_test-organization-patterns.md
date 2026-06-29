---
name: software-development_agent-fork-maintenance_references_test-organization-patterns
description: Test File Organization — Category Mapping
title: "Software Development Agent Fork Maintenance References Test Organization Patterns"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Test File Organization — Category Mapping |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Test File Organization — Category Mapping

After dead-file cleanup and before declaring "done," consolidate any remaining root-level `test_*.py` files into the proper `tests/` subdirectory.

## Category Rules

| Root Pattern | Target in `tests/` |
|-------------|-------------------|
| `test_*.py` (matching module in root) | `tests/test_<module>.py` |
| `test_<tool>*.py` | `tests/tools/test_<tool>.py` |
| `test_gateway*.py` | `tests/gateway/test_<platform>.py` |
| `test_windows*.py`, `test_tor*`, `test_ocr*` | `tests/windows/test_<feature>.py` |
| `test_agent_*.py` | `tests/hermes_reference/agent/test_<thing>.py` (upstream tests live here) |
| `test_benchmark*.py`, `test_performans*` | `tests/stress/test_<name>.py` |

## What NOT to move

- `tests/` is already the test directory — files inside it are already organized
- Hermes Reference tests (`tests/hermes_reference/`) — these come from upstream and should NOT be touched
- `conftest.py` (only one should exist, in `tests/` root)
- `__init__.py` files needed for package imports

## Verification After Move

```bash
# Count remaining in root — should be 0
ls test_*.py 2>/dev/null | wc -l

# Count what moved
ls tests/tools/*.py 2>/dev/null | wc -l
ls tests/windows/*.py 2>/dev/null | wc -l
```

Also clean up `__pycache__` from root after moving files:

```python
import shutil
from pathlib import Path
for cache_dir in Path(".").glob("**/__pycache__"):
    shutil.rmtree(cache_dir)
```
