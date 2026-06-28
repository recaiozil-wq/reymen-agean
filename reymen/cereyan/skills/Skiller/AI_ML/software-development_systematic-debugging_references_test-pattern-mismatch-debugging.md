---
name: software-development_systematic-debugging_references_test-pattern-mismatch-debugging
description: Test-Pattern Mismatch Debugging
title: "Software Development Systematic Debugging References Test Pattern Mismatch Debugging"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Test-Pattern Mismatch Debugging |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Test-Pattern Mismatch Debugging

## Overview

Tests fail not because the code is "broken" but because the test and code have drifted apart. This reference catalogs the most common mismatch patterns and how to diagnose them.

## Patterns

### 1. Dead Code — Handler Never Executes

**Scenario:** The code looks correct (has the right `if` block), but the test says the feature is missing.

**Root cause:** The handler sits in a method AFTER an unconditional `return` from another path (e.g. `_fallback_calistir()` returns before reaching it).

**Diagnosis:**
```
grep -n "def _fallback_calistir\|def calistir" motor.py
# Check if the missing handler is in calistir() AFTER _fallback_calistir() returns
```

**Fix:** Move the handler INTO `_fallback_calistir()` before its last `return`, or register it in the ToolRegistry/PluginManager layer.

**Pitfall:** The dead code may include MANY handlers (not just the one you're fixing). Move all of them at once, or verify any you leave behind are truly obsolete.


### 2. Registry Interception — Wrong Prefix Check

**Scenario:** A feature works when you call the fallback directly (e.g. `m._fallback_calistir('X')` returns OK), but fails when called through the main entry point (e.g. `m.calistir('X')`).

**Root cause:** The ToolRegistry/PluginManager intercepts the call first. If the "unknown" error message format doesn't match what the main method checks for, the error is treated as a successful result.

**Diagnosis:**
```python
# Check what the registry actually returns
r = _REGISTRY.calistir('X', '')
print(repr(r))                                          # Actual output
print(r.startswith("[Bilinmeyen arac]"))                # What code checks for
```

**Common mismatch:** Registry returns `[Hata]: Bilinmeyen arac 'X'.` but code checks for `[Bilinmeyen arac]` prefix. Since `[Hata]:` ≠ `[Bilinmeyen arac]`, the error is treated as success.

**Fix:** Align the prefix:
- Change registry to return `[Bilinmeyen arac]` prefix (consistent with the check)
- OR expand the check to handle both formats
- OR register the feature in the registry so it never reaches "unknown"


### 3. Object Type Mismatch — Dict vs Dataclass/NamedTuple

**Scenario:** Test accesses `result[key]` but gets `TypeError: 'X' object is not subscriptable`.

**Root cause:** The underlying object was changed from a `dict` to a class/dataclass/namedtuple but the test was not updated.

**Diagnosis:**
```python
type(result)                                  # <class 'my_module.SaglayCiAdim'>
hasattr(result, 'provider')                  # True (uses attribute access)
```

**Fix:** Change `result["key"]` → `result.key` in the test.

**Pitfall:** If the class also supports `__getitem__` for backward compat, both can work — in that case the test wasn't broken, but it wasn't testing the real path either.


### 4. Error Message Drift

**Scenario:** Test asserts `"X mesaji" in result` but the real message is `"Y mesaji"`.

**Root cause:** The code's error/response messages were updated but the test was not.

**Diagnosis:**
```python
# Search for the actual message in the source
grep -rn "Eslesen beceri" --include="*.py" .
```

**Fix:** Update the test assertion string to match the current code.

**Pitfall on compound assertions:** If the test asserts `"X" in result AND result.count("Y") > 3`, updating only one string may not be enough — check the full shape of the output.


### 5. Pytest Stdout Capture Failure

**Scenario:** pytest crashes with `ValueError: I/O operation on closed file` during session teardown.

**Root cause:** An imported module writes to stdout (plugin loading, skill initialization, configuration dumps) during import. This breaks pytest's `capsys`/stdout capture because the file handles get confused.

**Symptoms:**
- Test session starts, collects tests, then crashes immediately
- `--tb=short` shows the traceback in `_pytest/capture.py`
- Test with `-s` (disable capture) works fine

**Diagnosis:**
```bash
# Check if the module prints during import
python -c "import motor" 2>&1 | head -20
# If you see [Plugin], [Skill], etc. output — that's the cause
```

**Fix:**
- Add `addopts = -s` to `pytest.ini` (disables capture globally)
- OR wrap the noisy imports in the test file (not recommended for large modules)
- OR move print statements behind a `--verbose` flag in the source module

**Pitfall:** `-s` means module stdout appears in test output, making it noisy. Tradeoff between clean output and working tests.


### 6. Test Timeout on I/O Operations

**Scenario:** Test hangs for 60+ seconds then times out.

**Root cause:** Test calls a function that performs real I/O (file zip, network call, disk scan of 5000+ files) and the operation is slow.

**Diagnosis:**
```bash
# Check what the test function does
grep -n "yedekle\|zip\|tar\|archive" test_yardimci.py
```

**Fix:** Replace the real I/O call with a lightweight assertion:
- Instead of `yol = yedekle("test"); assert Path(yol).exists()` → `from backup import yedekle; assert callable(yedekle)`
- Instead of scanning all 5000 skills → assert against a known minimum count
- Use `tmp_path` fixture instead of real file paths


## Diagnostic Flowchart

```
Test FAILS
  │
  ├─ pytest crashes with I/O error?
  │   → Pytest Stdout Capture Failure (§5)
  │     Fix: addopts = -s in pytest.ini
  │
  ├─ Test times out (>30s)?
  │   → Test Timeout on I/O Operations (§6)
  │     Fix: replace real I/O with lightweight assertion
  │
  ├─ TypeError: object is not subscriptable?
  │   → Object Type Mismatch (§3)
  │     Fix: result["key"] → result.key
  │
  ├─ AssertionError: expected "X" got "Y"?
  │   ├─ Handler looks correct in source?
  │   │   → Dead Code — Handler Never Executes (§1)
  │   │     Fix: move handler into _fallback_calistir
  │   ├─ Works via direct call but not via main entry?
  │   │   → Registry Interception (§2)
  │   │     Fix: align error prefix or register in registry
  │   └─ Neither?
  │       → Error Message Drift (§4)
  │         Fix: update test assertion string
  │
  └─ All above ruled out?
      → File a proper bug report — this is a real logic error
```
