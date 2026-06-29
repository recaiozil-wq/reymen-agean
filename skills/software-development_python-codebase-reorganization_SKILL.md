---
name: software-development-python-codebase-reorganization
description: 'Move files from a flat root directory into a package hierarchy **without
  breaking a single import**. The trick: leave a tiny **shim** at the original path
  that re-exports everything from the new location.'
title: Software Development Python Codebase Reorganization
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

migration — move files without breaking any import.
# Python Codebase Reorganization (Shim-Based)

Move files from a flat root directory into a package hierarchy **without breaking a single import**. The trick: leave a tiny **shim** at the original path that re-exports everything from the new location.

## Workflow

### Phase 1: Inventory & Categorize

```bash
# Find all real (non-shim) .py files in root
python3 -c "
import os
real = [f for f in os.listdir('.') if f.endswith('.py') and f != '__init__.py' and os.path.getsize(f) >= 300]
print(f'{len(real)} real files')
"
```

**Categorize by function** (AI engine, system, tools, memory, security, network, etc.), **not** by import dependency.

> **Key insight:** You do NOT need to separate stdlib-only files from project-importing files. Shim files handle ALL backward compatibility — a moved file can still `from other_module import X` because the shim at `other_module.py` redirects to the new location. The shim resolves the import chain transitively.

That said, identifying stdlib-only files is useful for **batched automation** (simple shim, no risk of needing private-name exceptions):

```python
STDLIB = {'os','sys','json','re','time','math','logging','uuid',
          'pathlib','abc','dataclasses','enum','functools','collections',
          'datetime','contextlib','threading','asyncio','subprocess', ...}
```

### Phase 2: Single-Pass Migration (All Files)

Move ALL files to their packages in a single pass, creating shims as you go. This is safe because every shim acts as a backward-compatibility layer for ALL callers — both inside and outside the new package.

```python
import shutil, os

packages = {
    "cereyan": ["motor.py", "beyin.py", "planlayici.py", ...],
    "sistem":  ["main.py", "cli.py", "config_loader.py", ...],
    "hafiza":  ["session_db.py", "context_manager.py", ...],
    # ... all packages
}

total = 0
for pkg, files in packages.items():
    os.makedirs(f"reymen/{pkg}", exist_ok=True)
    with open(f"reymen/{pkg}/__init__.py", "w") as f:
        f.write(f'"""reymen/{pkg} — Description"""\\n')
    
    for f in files:
        if not os.path.exists(f):
            continue
        mod = f.replace(".py", "")
        shutil.move(f, f"reymen/{pkg}/{f}")
        # Create the shim
        with open(f, "w") as shim:
            shim.write(f"from reymen.{pkg}.{mod} import *  # noqa: F401, F403\\n")
        total += 1

print(f"✅ {total} files moved, 0 real files remaining in root")
```

### Phase 3: Fix shim for private names

**CRITICAL PITFALL:** `import *` does NOT export names starting with `_`. If a test imports `_private_function`, the shim needs an explicit re-export:

```python
# In the shim file:
from reymen.paket_adi.modul import *  # noqa: F401, F403
from reymen.paket_adi.modul import _private_function  # noqa: F401, F403  # ← explicit
```

### Phase 4: Fix imports for test suites

After reorganization, test files may still import from the old root-level names. If you have hundreds of broken imports across `tests/`, see `project-first-run`'s [bulk-import-resolution reference](../project-first-run/references/bulk-import-resolution.md) for systematic categorization and per-type fix strategies (conftest stubs, root shim creation, Unix-only handling).

### Verify

After each batch:

```bash
# 1. All shims import without error
python3 -c "
for m in ['module1', 'module2', ...]:
    mod = __import__(m)
    symbols = len([x for x in dir(mod) if not x.startswith('_')])
    print(f'{m}: {symbols} symbols')
"

# 2. Full test suite passes
python -m pytest tests/ -q --tb=short -s 2>&1 | grep -E 'passed|failed|error'
```

## Batch ordering

Since shims handle ALL cross-file imports, **you don't need a special order**. Move all files in one batch.

If you prefer incremental batches for safety:

1. **stdlib-only modules** — zero shim complexity, batch first
2. **Remaining modules** — all move identically; shims resolve cross-references

## Pitfalls

| Issue | Symptom | Fix |
|-------|---------|-----|
| Private names missing | `ImportError: cannot import name '_foo'` | Add explicit `from pkg.mod import _foo` to shim |
| Shim-transitive import appears broken | RuntimeError after move | This is actually RARE — the shim at root resolves the chain. If it fails, the target module has a **real** circular import that was latent before the move. Break the cycle by deferring one import inside a function. |
| Circular import surfaced by move | RuntimeError: cannot import name X from partially initialized module | Same as above — was always present but latent. Use lazy import (`def fn(): from X import Y`) |
| `__init__.py` confuses test discovery | Tests disappear or error | Check namespace `__path__` in __init__.py files — either list both paths or move incompatible tests elsewhere |
| **Directory shadows module shim** | `ImportError` / wrong module loaded | When a **directory package** (`some_module/`) exists alongside a **shim** (`some_module.py`), Python's import system prefers the directory — the shim is invisible. **Fix:** either (a) integrate the shim's re-exports into the directory's `__init__.py`, or (b) rename the shim to avoid the conflict. Check with `ls -la some_module*` to see if both a file and a directory exist. |
| Shim too small | Pytest collection error | Shim file must be valid Python; `import *` from package that exists |
| Missed stdlib module | False positive in dependency scan | Keep the STDLIB set comprehensive — check with `python3 -c "import sys; print('stdlib' if 'sys' in sys.stdlib_module_names else 'external')"` (Python 3.10+) |

## Verification checklist

- [ ] All shims import without error
- [ ] All shims expose expected symbols
- [ ] `pytest tests/` passes same count as before
- [ ] **Symmetry check:** number of shims in root == number of `.py` files in all packages (excl. `__init__.py`)
- [ ] **Every shim points to a real file** — check with script:
  ```python
  import os
  root_shims = [f for f in os.listdir('.') if f.endswith('.py') and f != '__init__.py']
  for f in root_shims:
      with open(f) as fh:
          for line in fh:
              if 'from reymen.' in line:
                  target = line.split()[1].replace('.', '/') + '.py'
                  assert os.path.exists(target), f"{f} -> {target} NOT FOUND"
  ```
- [ ] `reymen/__init__.py` still works (if it re-exports from moved modules)
- [ ] **Optional optimization:** Update `reymen/__init__.py` to import directly from new package paths instead of relying on shims, e.g. `from reymen.cereyan.motor import Motor` instead of `from motor import Motor`. This reduces shim dependency and makes the package self-contained. Safe to defer or skip — shims handle it.
- [ ] Main application starts without ImportError
