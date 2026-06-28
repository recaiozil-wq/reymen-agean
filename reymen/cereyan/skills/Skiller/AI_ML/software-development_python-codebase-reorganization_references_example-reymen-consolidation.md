---
name: software-development_python-codebase-reorganization_references_example-reymen-consolidation
description: ReYMeN Codebase Consolidation — Reference Example
title: "Software Development Python Codebase Reorganization References Example Reymen Consolidation"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | ReYMeN Codebase Consolidation — Reference Example |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# ReYMeN Codebase Consolidation — Reference Example

## Scope

ReYMeN: a fork of Hermes Agent with 159 root `.py` files (all moved). No breakage, 243 tests passing.

## Package Design

| Package | Files | Content |
|---------|-------|---------|
| `reymen/ag/` | 10 | Network, gateway, MCP oauth, providers |
| `reymen/arac/` | 27 | Tool implementations (`araclar_*`, MCP, executors) |
| `reymen/cereyan/` | 34 | AI engine: `motor`, `beyin`, planning, learning |
| `reymen/guvenlik/` | 12 | Security: guardrails, sandbox, threat detection |
| `reymen/hafiza/` | 15 | Memory: `hafiza`, context, session, vectors |
| `reymen/sistem/` | 51 | System: `main`, CLI, config, bootstrap |
| `reymen/windows/` | 9 | Windows automation: Tor, nisan, screenshot |

## Migration Script (Python, in-place)

```python
import shutil, os

packages = {
    "cereyan": ["motor.py", "beyin.py", "alt_ajan.py", ...],  # 20 files
    "sistem":  ["main.py", "cli.py", "config_loader.py", ...], # 30 files
    "ag":      ["gateway_runner.py", "acp_server.py", ...],    # 10 files
    "windows": ["tor_otomasyonu.py", "windows_events.py", ...],# 5 files
    "arac":    ["araclar_web.py", "execute_code_tool.py", ...], # 11 files
}

for pkg, files in packages.items():
    os.makedirs(f"reymen/{pkg}", exist_ok=True)
    with open(f"reymen/{pkg}/__init__.py", "w") as f:
        f.write(f'"""reymen/{pkg} — Description"""\n')
    for f in files:
        mod = f.replace(".py", "")
        shutil.move(f, f"reymen/{pkg}/{f}")
        with open(f, "w") as shim:
            shim.write(f"from reymen.{pkg}.{mod} import *  # noqa: F401, F403\n")
```

## Shim Anatomy

Each shim is a single redirect line:

```python
# -*- coding: utf-8 -*-
# SHIM — reymen/cereyan/motor.py yonlendirir
from reymen.cereyan.motor import *  # noqa: F401, F403
```

Exception: if a test imports a private name (`_guvenlik_kontrol`), add an explicit second line:

```python
from reymen.arac.execute_code_tool import *  # noqa: F401, F403
from reymen.arac.execute_code_tool import _guvenlik_kontrol  # noqa: F401, F403
```

## Verification Script

```python
import os

root_shims = [f for f in os.listdir('.') if f.endswith('.py') and f != '__init__.py']
print(f"Root shims: {len(root_shims)}")

# Check every shim targets a real file
for f in root_shims:
    with open(f) as fh:
        for line in fh:
            if 'from reymen.' in line:
                target = line.split()[1].replace('.', '/') + '.py'
                assert os.path.exists(target), f"MISSING: {f} -> {target}"

# Count files in all packages
total_in_pkg = 0
for pkg_dir in glob.glob("reymen/*/"):
    pkg_name = os.path.basename(os.path.normpath(pkg_dir))
    if pkg_name == "__pycache__":
        continue
    count = len([f for f in os.listdir(pkg_dir) if f.endswith('.py') and f != '__init__.py'])
    total_in_pkg += count

assert total_in_pkg == len(root_shims), f"{total_in_pkg} pkg != {len(root_shims)} shims"
print("✅ Symmetry: shims == packages")
```

## Key Lessons

1. **Shims handle transitive imports.** A file moved to `reymen/cereyan/motor.py` can still `from beyin import Beyin` — the shim at root `beyin.py` resolves it. No import rewrites needed inside moved files.
2. **Batch everything in one pass.** Don't waste time categorizing by stdlib vs project imports. Phase 1 categorization is for PACKAGE ASSIGNMENT, not import safety.
3. **Private names are the only edge case.** `_prefix` symbols aren't re-exported by `import *`. Tests importing them need the explicit re-export in the shim.
4. **Test namespace `__path__` must include both locations.** If a test directory uses `__init__.py` with a `__path__` redirect, pytest won't discover local test files. See `agent-fork-maintenance` Phase 8b.
5. **Directory shadows module shim.** If a `telegram_bot/` directory (package) exists alongside a `telegram_bot.py` shim, Python's import system prefers the directory — the shim becomes invisible. **Fix:** Remove the directory's `__init__.py` (if the dir was created by mistake), integrate the shim's re-exports into the directory's `__init__.py`, or rename the shim to avoid the conflict. Detect with `ls -la telegram_bot*` to check for both file and directory.
6. **Package file count should exactly equal root shim count.** Run the symmetry check as the final verification step.
