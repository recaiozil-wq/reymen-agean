---
name: software-development_error-handling-audit_references_syntax-corruption-pattern
description: "Regex Syntax Corruption — `except X: as _var:` Pattern"
title: "Software Development Error Handling Audit References Syntax Corruption Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Regex Syntax Corruption — `except X: as _var:` Pattern |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Regex Syntax Corruption — `except X: as _var:` Pattern

## The Problem

Batch find-and-replace of `except Exception:\n    pass` → `except Exception as _e:\n    print(...)` can produce **invalid Python syntax** if the regex is wrong.

### Invalid output:
```python
except Exception: as _e:
    print(...)
```

This is a `SyntaxError` because `Exception:` with a colon followed by `as` is invalid. The colon before `as` must be removed.

## Root Cause

Templates with `except X:\n    pass` get matched by regexes like:
```
r'except (\w+):\s+as\s+(_\w+):'
```

But this fails on:
- **Dotted types**: `except json.JSONDecodeError:` → `\w+` doesn't match the dot
- **Tuple types**: `except (OSError, ValueError):` → parentheses not matched
- **Bare except**: `except: as _var:` → no type at all

## Fix (Comprehensive)

```python
import re

# Step 1: Remove spurious colon before 'as' in all except variants
content = re.sub(
    r'(except[^:]*?):\s+as\s+(_\w+):',
    r'\1 as \2:',
    content
)

# Step 2: Fix bare 'except: as _var:' -> 'except Exception as _var:'
content = re.sub(
    r'except:\s+as\s+(_\w+):',
    r'except Exception as \1:',
    content
)

# Step 3: Fix indentation of lines after except blocks
lines = content.split("\n")
for i, line in enumerate(lines):
    stripped = line.strip()
    if "except" in stripped and " as _" in stripped and stripped.endswith(":"):
        indent = len(line) - len(line.lstrip())
        expected = indent + 4
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j < len(lines) and lines[j].strip():
            actual = len(lines[j]) - len(lines[j].lstrip())
            if actual < expected:
                lines[j] = " " * expected + lines[j].lstrip()
```

## Verification

```bash
python -c "
from pathlib import Path
for f in Path('.').glob('*.py'):
    try:
        compile(f.read_text(), f.name, 'exec')
    except SyntaxError as e:
        print(f'FAIL: {f.name}:{e.lineno} - {e.msg}')
"
```
