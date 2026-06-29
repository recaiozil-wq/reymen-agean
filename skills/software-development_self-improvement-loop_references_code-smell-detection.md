---
name: software-development_self-improvement-loop_references_code-smell-detection
description: Code Smell Detection Patterns (Alan 3)
title: "Software Development Self Improvement Loop References Code Smell Detection"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Code Smell Detection Patterns (Alan 3) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Code Smell Detection Patterns (Alan 3)

## RECOMMENDED: Reusable Script

**Use `scripts/code_quality_scan.py`** instead of inline one-liners.
It combines all 5 checks in a single run with a clean report:

```bash
python3 /path/to/code_quality_scan.py --proj /path/to/project
python3 /path/to/code_quality_scan.py --proj . --fix-bom         # auto-fix BOM
python3 /path/to/code_quality_scan.py --proj . --exclude "venv,bot_venv"  # custom skip
```

Advantages over one-liners:
- No nested-quote escaping problems (common pitfall in cron jobs)
- `--fix-bom` flag for one-step fix
- Exclude-list parameter instead of hardcoded dirs
- Parsable summary line at end
- Handles syntax-error/bare-except overlap correctly (BOM-caused parse failures aren't misreported as bare-except)


## One-Liner Reference (for quick checks)

Below are the individual one-liners for manual/quick use. Prefer the script above for full iterations.

## 1. Bare `except:` Detection via AST

`search_files` with regex `except\\s*:` is unreliable:
- Truncated at 50 files per call in count mode
- Can't distinguish bare `except:` from `except Exception:`
- Misses files where `except:` spans multiple lines

**Use `ast.walk()` instead:**

```python
python3 -c "
import ast, os
bare = []
for root, dirs, files in os.walk('tools'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__','venv','.git')]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        try:
            with open(path, encoding='utf-8') as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and node.type is None:
                    bare.append(path); break
        except SyntaxError as e:
            print(f'SYNTAX: {path}: {e}')
        except: pass
for p in sorted(set(bare)):
    print(f'  {p}')
print(f'Total: {len(set(bare))}')
"
```

For multiple directories, expand `os.walk()` loops or add dirs to a list.

## 2. BOM (UTF-8 Byte Order Mark) Detection & Fix

BOM bytes: `\xef\xbb\xbf` at file start. Python 3.10+ handles BOM transparently but:
- AST parser may report `invalid non-printable character U+FEFF`
- linters (pylint, flake8) may fail
- CI tools on POSIX may choke

**Detection:**

```python
python3 -c "
import os
for root, dirs, files in os.walk('tools'):
    dirs[:] = [d for d in dirs if d not in ('__pycache__','venv','.git')]
    for f in files:
        if not f.endswith('.py'): continue
        path = os.path.join(root, f)
        with open(path, 'rb') as fh:
            data = fh.read(5)
        if data[:3] == b'\xef\xbb\xbf':
            print(f'BOM: {path}')
"
```

**Fix (strip BOM):**

```python
python3 -c "
for f in ['file1.py', 'file2.py']:
    with open(f, 'rb') as fh:
        data = fh.read()
    if data[:3] == b'\xef\xbb\xbf':
        with open(f, 'wb') as fh:
            fh.write(data[3:])
        print(f'Fixed: {f}')
"
```

## 3. Syntax Error Check (after BOM strip)

```python
python3 -c "
import py_compile
for f in ['tools/skills_hub.py', 'tools/tool_backend_helpers.py']:
    try:
        py_compile.compile(f, doraise=True)
        print(f'{f}: OK')
    except py_compile.PyCompileError as e:
        print(f'{f}: FAIL: {e}')
"
```

Also verify imports work:
```python
python3 -c "
import importlib, sys
sys.path.insert(0, '.')
for mod in ['tools.skills_hub', 'tools.tool_backend_helpers']:
    try:
        importlib.reload(__import__(mod))
        print(f'{mod}: IMPORT OK')
    except Exception as e:
        print(f'{mod}: FAIL: {e}')
"
```

## 4. TODO/FIXME/HACK/XXX Count

```python
python3 -c "
import re, os
patterns = {k:0 for k in ['TODO','FIXME','HACK','XXX']}
for root, dirs, files in os.walk('.'):
    if 'venv' in root.split(os.sep) or '__pycache__' in root: continue
    dirs[:] = [d for d in dirs if d not in ('__pycache__','venv','.git')]
    for f in files:
        if not f.endswith('.py'): continue
        try:
            with open(os.path.join(root,f), errors='replace') as fh:
                for line in fh:
                    for k in patterns:
                        if re.search(r'#\s*'+k+r'\b', line):
                            patterns[k] += 1
        except: pass
for k,v in patterns.items():
    print(f'{k}: {v}')
"
```

## 5. Priority: search_files vs Script vs AST

| Approach | Best For | Limitation |
|----------|----------|------------|
| `search_files(pattern=..., output_mode='count')` | First pass, broad coverage | 50-file limit per page, regex-only |
| `scripts/code_quality_scan.py` | Full iteration (preferred) | Requires write_file + terminal |
| `ast.walk()` one-liner | Quick manual check | Nested-quote escaping issues |
| `py_compile.compile()` | Syntax validation | Doesn't check import semantics |
| `python3 -c "__import__(mod)"` | Import path validation | Only checks top-level |
