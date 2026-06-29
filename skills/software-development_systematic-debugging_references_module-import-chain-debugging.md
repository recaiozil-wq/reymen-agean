---
name: software-development_systematic-debugging_references_module-import-chain-debugging
description: Module Import Chain Debugging
title: "Software Development Systematic Debugging References Module Import Chain Debugging"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Module Import Chain Debugging |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Module Import Chain Debugging

Systematic approach to diagnosing and fixing broken Python module imports in forked or mixed-source projects.

## When to Use

- A project contains code from multiple sources (original + fork + copies) with diverging import chains
- Import errors cascade through deep dependency chains: `A → B → C → ❌`
- `ModuleNotFoundError` or `ImportError` for names that "should exist"
- A Python file shadows a same-named package directory

## The Systematic Method

### Phase 1: Inventory

Start by understanding what you're working with:

```bash
# All .py files (exclude venv/cache)
find . -name '*.py' -not -path '*/venv/*' -not -path '*/__pycache__/*' | wc -l

# Identify original vs fork files: which files DON'T exist in the source project
# Compare against the original project's file list
for f in fork_file_list; do
  test -f "original/$f" && echo "ORIGINAL: $f" || echo "FORK_ONLY: $f"
done
```

### Phase 2: Batch Import Test

Write a script that tests every import systematically, categorized as:
- **OK** — imports and functions normally
- **IMPORT_HATASI** — fails at `import`/`from` statement
- **RUNTIME_HATASI** — imports but fails when actually used

```python
# Pattern:
for mod_adi in module_list:
    try:
        __import__(mod_adi)
        # Runtime test (try to instantiate/call it)
        try:
            results["OK"].append(mod_adi)
        except Exception as e:
            results["RUNTIME_HATASI"].append((mod_adi, str(e)))
    except Exception as e:
        results["IMPORT_HATASI"].append((mod_adi, str(e)))
```

### Phase 3: Trace Import Chain

For each broken module, find the exact failure point.

Read the traceback from **BOTTOM to TOP** — the last frame is the ROOT CAUSE.

```
  File "C.py", line 10 → from tools.registry import tool_error    ← ROOT CAUSE
  File "B.py", line 5  → from C import something                  ← INTERMEDIATE
  File "A.py", line 3  → from B import something                  ← SYMPTOM
```

Fix the ROOT CAUSE first. The symptoms disappear automatically.

### Phase 4: Three Common Fix Patterns

#### Pattern A: File vs Package Name Conflict

**Symptom:** `No module named 'X.config'; 'X' is not a package`

**Cause:** `X.py` (file) shadows `X/` (package directory). Python finds the file first.

**Fix:** Rename the file so the package directory is discovered:
```bash
mv X.py X_bridge.py
```

**Verify:** `python -c "from X.config import cfg_get; print('OK')"`

#### Pattern B: Missing Compatibility Function

**Symptom:** `ImportError: cannot import name 'tool_error' from 'tools.registry'`

**Cause:** Forked project renamed/restructured modules, but consumers still import old names.

**Fix:** Add a compatibility shim:
```python
def tool_error(message, success=False):
    """Compatibility shim for projects that import this from the original."""
    return json.dumps({"success": success, "error": message}, ensure_ascii=False)
```

**Common Hermes-compatibility shims:**
| Function | Module | Purpose |
|----------|--------|---------|
| `tool_error()` | `tools.registry` | Error response format |
| `get_definitions()` | `ToolRegistry` method | Tool schema listing |
| `scan_for_threats()` | `tools.threat_patterns` | Security scanning |
| `first_threat_message()` | `tools.threat_patterns` | Security alert |

#### Pattern C: Class/Function Name Mismatch

**Symptom:** `ImportError: cannot import name 'VektorelHafiza' from 'vektorel_hafiza'`

**Fix:** Discover actual names:
```bash
python -c "import vektorel_hafiza; print([x for x in dir(vektorel_hafiza) if not x.startswith('_')])"
```

### Phase 5: Dependency Depth Check

Not all broken modules matter. Check if main.py actually reaches them:

```bash
grep -n "^from\|^import" main.py
```

**Rule:** Hermes `agent/` internal modules with deep chains are often dead code in forks. Only fix what the app entry point actually imports.

## Verification

After fixes:
```bash
python -m pytest test_learning_loop.py -v
# Should pass
```

Full module re-test:
```bash
python modul_test_script.py
# OK count should increase, broken count should decrease
```
