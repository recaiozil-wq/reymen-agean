---
name: software-development_agent-fork-maintenance_references_branding-rename-pattern
description: Branding Rename Pattern (Hermes → ReYMeN)
title: "Software Development Agent Fork Maintenance References Branding Rename Pattern"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Branding Rename Pattern (Hermes → ReYMeN) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Branding Rename Pattern (Hermes → ReYMeN)

Systematic approach for renaming an upstream project's brand references to the fork's brand. Designed for the ReYMeN (Hermes Agent fork) context but generalizes.

## Scope Rules

| Change | Context | Examples |
|--------|---------|---------|
| ✅ **Always rename** | Fork's own code: comments, docstrings, file/dir names, test paths | `hermes_memory_buda()` → `reymen_memory_buda()`, `tests/hermes_reference/` → `tests/ReYMeN_reference/` |
| ✅ **Always rename** | Internal function/variable names with "hermes" prefix | `hermes_bot` → `reymen_bot`, `_HERMES_CORE_TOOLS` → `_REYMEN_CORE_TOOLS` |
| ❌ **Never rename** | Actual system paths | `~/AppData/Local/hermes/`, `C:\Users\...\hermes\` |
| ❌ **Never rename** | Environment variables | `HERMES_HOME`, `HERMES_API_KEY`, `HERMES_KANBAN_TASK` |
| ❌ **Never rename** | Installed Python packages | `hermes_cli`, `hermes-agent` |
| ❌ **Never rename** | Upstream backup directories | `agent/` (Hermes upstream source backup) |
| ❌ **Never rename** | Third-party references | `OpenHermes` model name, numpy `hermite` polynomials |
| ❌ **Never rename** | GitHub repo URLs | `github.com/nousresearch/hermes-agent.git` |

## Rename Order (Always This Sequence)

### Step 1: Directories First

Rename directories **before** fixing code references — otherwise the path won't resolve.

```bash
# Core directories
mv tests/hermes_reference tests/ReYMeN_reference
mv reymen/hermes reymen/ReYMeN_mirror

# Files
mv tools/hermes_ajan.py tools/reymen_ajan.py
mv .hermes_sync.sh .ReYMeN_sync.sh
mv hermes-full-backup ReYMeN-full-backup
```

### Step 2: Path References in Code

Update all string/file-path references to the renamed paths:

```python
REPLACEMENTS = {
    "hermes_reference": "ReYMeN_reference",
    ".hermes_sync.sh": ".ReYMeN_sync.sh",
    "hermes-full-backup": "ReYMeN-full-backup",
    "tools/hermes_ajan": "tools/reymen_ajan",
}

import os
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ('venv', '__pycache__', 'agent', '.git', 'ReYMeN-full-backup')]
    for f in files:
        if not f.endswith(('.py', '.sh', '.md', '.yaml', '.json', '.txt')):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as fh:
                content = fh.read()
        except: continue
        
        new_content = content
        for old, new in REPLACEMENTS.items():
            new_content = new_content.replace(old, new)
        
        if new_content != content:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            print(f"  ✅ {path}")
```

### Step 3: Comment/Docstring "Hermes" → "ReYMeN"

Only in the fork's own code (skip `venv/`, `agent/`, `ReYMeN-full-backup/`):

```python
import re

EXCLUDE_DIRS = {'venv', '__pycache__', 'agent', 'ReYMeN-full-backup', 'ReYMeN_mirror', '.git'}
EXCLUDE_PATTERNS = ['openhermes', 'hermite', 'appdata', 'local/hermes', 'hermes_projesi', 'hermes_cli']

for root, dirs, files in os.walk(SOURCE_DIRS):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        with open(path, 'r') as fh:
            content = fh.read()
        
        new_content = content
        # Replace word-boundary "Hermes" in comments/docstrings
        new_content = re.sub(r'\bHermes\b', 'ReYMeN', new_content)
        new_content = re.sub(r'\bhermes\b', 'reymen', new_content)
        
        # Revert false positives
        for pattern in EXCLUDE_PATTERNS:
            if pattern in new_content.lower():
                # This is too risky to automate — manual review needed
                pass
```

**Safer approach:** Only change lines that are clearly comments or string literals:

```python
for i, line in enumerate(content.split('\n')):
    stripped = line.strip()
    if stripped.startswith('#') or '"""' in stripped or "'''" in stripped:
        if not any(x in stripped.lower() for x in EXCLUDE_PATTERNS):
            new_line = re.sub(r'\bHermes\b', 'ReYMeN', line)
            new_line = re.sub(r'\bhermes\b', 'reymen', new_line)
```

### Step 4: Internal Function/Variable Names

Change function and variable names that use "hermes" as a prefix:

```python
FUNCTION_RENAMES = {
    'hermes_memory_buda': 'reymen_memory_buda',
    '_HERMES_CORE_TOOLS': '_REYMEN_CORE_TOOLS',
    'hermes_bot': 'reymen_bot',
    'HERMES_MEMORIES': 'REYMEN_MEMORIES',
    'HERMES_CONFIG': 'REYMEN_CONFIG',
    'HERMES_HOME': 'REYMEN_HOME_PATH',
    'HERMES_ENV': 'REYMEN_ENV',
    'HERMES_DBS': 'REYMEN_DBS',
}
```

Check for callers of renamed functions — `grep -rn 'hermes_memory_buda' reymen/` — and update them.

### Step 5: Test `__init__.py` Namespace Paths

```python
# Before (broken after rename — path doesn't exist):
__path__ = [str(Path(__file__).parent.parent / "hermes_reference" / "tools")]

# After:
__path__ = [
    str(Path(__file__).parent),  # Local tests first
    str(Path(__file__).parent.parent / "ReYMeN_reference" / "tools"),
]
```

## Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Directory shadows module shim | `telegram_bot/` dir + `telegram_bot.py` shim coexist | Integrate shim re-exports into `telegram_bot/__init__.py` |
| `from hermes_cli import` broken | Package name is `hermes_cli` (installed dep, not our code) | Don't change import lines with `hermes_cli` |
| `from agent/hermes_*` broken after rename | `agent/` is upstream backup, should not be renamed | Keep `agent/` as-is |
| Renamed function callers missed | Something calls `hermes_memory_buda()` that you forgot | `grep -rn 'old_name' reymen/` before and after |
| False positive in numpy `hermite` | numpy's `hermite_e.py` has `hermesub`, `hermemul` functions | Exclude all `numpy/polynomial/` paths |
| "OpenHermes" model reference changed | "Hermes" → "ReYMeN" also matched model name | Exclude lines with `OpenHermes` |
| VENV paths in `reymen/ReYMeN_mirror/venv/` | Absolute paths in pyvenv.cfg not affected by folder rename | No action needed — venv uses absolute interpreter paths |
