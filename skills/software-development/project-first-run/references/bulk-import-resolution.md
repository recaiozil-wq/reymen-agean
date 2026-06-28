# Bulk Import Error Resolution

Resolve hundreds of `ImportError` / `ModuleNotFoundError` across a large test suite (or codebase) by systematic categorization and per-type fix strategy.

## When to Use

- First run of a large project produces hundreds of import errors
- A codebase reorganization left test files broken
- A fork/rename left stale module references
- You need ALL tests importable before you can tell real failures from infrastructure noise

## Scanning Protocol

### 1. Extract Unique Imports

Scan all `.py` files, extracting the top-level module name from each `import X` and `from X import Y` statement:

```python
imports = set()
for root, dirs, files in os.walk('tests'):
    for f in files:
        if not f.endswith('.py'):
            continue
        path = os.path.join(root, f)
        try:
            with open(path, encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
        except:
            continue
        for line in content.splitlines():
            s = line.strip()
            if s.startswith('import '):
                parts = s.split()
                if len(parts) > 1:
                    mod = parts[1].split('.')[0].split(',')[0].split(' as')[0].strip()
                    if mod not in ('__future__',):
                        imports.add(mod)
            elif s.startswith('from ') and ' import ' in s:
                parts = s.split()
                if len(parts) > 1:
                    mod = parts[1].split('.')[0].strip()
                    if mod and mod != '__future__':
                        imports.add(mod)
```

> **Pitfall:** Line-based parsing captures `or`, `it`, `side`, `path` from multi-import lines like `import os, sys, json`. Filter these known artifacts:
> ```python
> KNOWN_ARTIFACTS = {'or', 'it', 'side', 'path', 'nonexistent_module'}
> ```

### 2. Resolve Each Module

```python
failed = {}
for mod in sorted(imports):
    try:
        __import__(mod)
    except Exception as e:
        failed[mod] = str(e)[:80]
```

### 3. Categorize Failures

| Category | Example | Fix Strategy |
|----------|---------|-------------|
| **External pip packages** | `botocore`, `numpy`, `qrcode`, `tiktoken`, `watchdog`, `lark-oapi`, `mautrix` | `pip install <pkg>` |
| **Unix-only stdlib** | `pwd`, `curses` → `_curses`, `pty` → `termios` | Add dummy modules to `conftest.py` (Windows only) |
| **Renamed/refactored modules** | `reymen_agent` → `reymen/` package, `anayasa_denetcisi` | Create root-level stub/shim that re-exports from real location |
| **Internal modules in subdirs** | `auxiliary_client` (in `agent/`), `delegate_task_tool` (in `tools/`) | Create root-level shim: `from agent.auxiliary_client import *` |
| **Runtime-only modules** | `hermes_tools` (only available inside Hermes agent context) | File must exist for import, but runtime provides resolution; accept as expected |
| **Parsing artifacts** | `or`, `it`, `side`, `path`, `nonexistent_module` | Skip — not real imports |

## Per-Category Fix Strategies

### 1. Unix-Only Modules → conftest.py

In the root `tests/conftest.py`, add:

```python
import types
for _unix_mod in ('termios', 'curses', 'pwd'):
    if _unix_mod not in sys.modules:
        try:
            __import__(_unix_mod)
        except ImportError:
            sys.modules[_unix_mod] = types.ModuleType(_unix_mod)
```

This prevents `ImportError` on Windows without changing any test file.

### 2. Subdirectory Internal Modules → Root Shims

When `agent/auxiliary_client.py` exists but `import auxiliary_client` fails:

```python
# Create at project root: auxiliary_client.py
# -*- coding: utf-8 -*-
"""SHIM — agent/auxiliary_client.py yönlendirir"""
from agent.auxiliary_client import *  # noqa: F401, F403
```

Also add the subdirectory to `sys.path` in conftest.py so the shim's target resolves:

```python
for _sub in ['agent', 'tools', 'plugins']:
    _p = str(PROJECT_ROOT / _sub)
    if _p not in sys.path:
        sys.path.insert(0, _p)
```

### 3. Missing ReYMeN/Fork Modules → Create Stub Implementations

When a module doesn't exist anywhere but tests need it (e.g. `reymen_agent`, `sistem_talimati`, `anayasa_denetcisi`):

1. Read the test file to understand the expected API (imports, function signatures, constants)
2. Create a minimal functional implementation
3. Use **sub-agents in parallel** (up to 3 at a time) to create multiple stubs simultaneously

Example stub creation flow:

```bash
# Categorize -> Batch into sub-agents -> Verify
delegate_task(tasks=[{goal: "create module1.py", context: "..."}, {goal: "create module2.py", ...}, {goal: "create module3.py", ...}])
```

### 4. External Packages → Install

```bash
pip install botocore numpy qrcode tiktoken tomli watchdog lark-oapi mautrix
```

For large batches, install with `--no-deps` and check each independently to isolate failures.

## Verification Loop

After each fix batch, re-run the scanner:

```bash
python -c "
# same scan loop as above
failed = {}
for mod in previously_failed:
    try:
        __import__(mod)
    except Exception as e:
        failed[mod] = str(e)[:60]
print(f'Remaining: {len(failed)} / {len(previously_failed)}')
"
```

Target: **0 import failures** for the entire test suite (excluding runtime-only modules and known artifacts).

## Pitfalls

1. **`import *` doesn't export private names** — If a test imports `_private_func` from a shim file, the shim needs an explicit re-export:
   ```python
   from agent.auxiliary_client import *  # noqa: F401, F403
   from agent.auxiliary_client import _private_func  # noqa: F401
   ```

2. **Plugin system loading during import scan** — If the project auto-loads plugins on import (Hermes Agent pattern), the scan takes too long. Either skip plugin modules or use `--help`-style detection:
   ```python
   imports.discard('plugins')  # Skip heavy plugin modules in scan
   ```

3. **`__init__.py` shadowing** — If a directory package has the same name as a root shim, Python prefers the directory. The shim is invisible. Either integrate into the `__init__.py` or rename.

4. **Sub-agent stub creation** — Sub-agents may produce incorrect imports (e.g. `from plugins/platforms/discord.voice_mixer` with `/` instead of `.`). Always verify after sub-agent batch.
