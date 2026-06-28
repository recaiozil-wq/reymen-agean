---
name: software-development-python-error-handling-audit
description: 'Audit and fix lazy error handling in Python codebases. Finds silent
  `except: pass`'
title: Software Development Python Error Handling Audit
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

pass blocks, bare excepts, and improperly caught exceptions. Batch-fix across entire
  project using Python scripts and regex. Verify syntax after every change.
# Python Error Handling Audit

Audit and fix lazy error handling in Python codebases. Finds silent `except: pass`
blocks, bare excepts, and improperly caught exceptions across an entire project.

## Workflow

### Phase 1: Discovery

Find all silent except blocks:

```bash
grep -rn "except.*:\s*$" *.py | grep -A1 "^" | grep -B1 "^pass$"
```

Or use Python for precision:

```python
from pathlib import Path
proj = Path(".")
for py in proj.glob("*.py"):
    lines = py.read_text().split("\n")
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("except") and i < len(lines):
            if lines[i].strip() == "pass":
                print(f"{py.name}:{i} | {s}")
```

### Phase 2: Fix Silent Blocks

**Pattern:** `except X:\n    pass` → `except X as _e:\n    log/print(_e)`

For a single file: use `patch` tool.
For bulk fix across 50+ files: use `execute_code` with regex:

```python
import re
from pathlib import Path

proj = Path(".")
for py in proj.glob("*.py"):
    content = py.read_text(encoding="utf-8", errors="replace")
    new = re.sub(
        r"except (\w+(?:\([^)]*\))?):\s+as\s+(_\w+):",
        r"except \1 as \2:",
        content
    )
    # Fix indentation after except blocks
    lines = new.split("\n")
    modified = False
    for i in range(len(lines)):
        s = lines[i].strip()
        if "except" in s and " as _" in s and s.endswith(":"):
            indent = len(lines[i]) - len(lines[i].lstrip())
            expected = indent + 4
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip():
                actual = len(lines[j]) - len(lines[j].lstrip())
                if actual < expected:
                    lines[j] = " " * expected + lines[j].lstrip()
                    modified = True
    if modified:
        py.write_text("\n".join(lines), encoding="utf-8")
```

### Phase 3: Syntax Verification

After ALL changes, verify every `.py` file compiles:

```python
from pathlib import Path
proj = Path(".")
ok = fail = 0
for py in sorted(proj.glob("*.py")):
    try:
        compile(py.read_text(encoding="utf-8"), py.name, "exec")
        ok += 1
    except SyntaxError as e:
        fail += 1
        print(f"ERROR {py.name}: {e}")
print(f"OK {ok} | FAIL {fail}")
```

Run this AFTER every bulk change. Do not skip this step.

### Phase 4: Fix Indentation Artifacts

If syntax fails with "expected an indented block after 'except' statement",
the auto-fixer may have left the next line under-indented. Fix it:

```python
for i in range(len(lines)):
    s = lines[i].strip()
    if s.startswith("except ") and " as _" in s and s.endswith(":"):
        indent = len(lines[i]) - len(lines[i].lstrip())
        expected = indent + 4
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j < len(lines) and lines[j].strip():
            if len(lines[j]) - len(lines[j].lstrip()) < expected:
                lines[j] = " " * expected + lines[j].lstrip()
```

## Common Patterns to Fix

| Before | After | Notes |
|--------|-------|-------|
| `except Exception:` then `pass` | `except Exception as _e:` then `logger.warning(...)` | Best — proper logging |
| `except ImportError:` then `pass` | `except ImportError:` then `# module optional, skipping` | Acceptable with comment |
| `except: pass` | `except Exception as _e:` then `print(f"unexpected error: {_e}")` | Never bare except |
| `except X, Y:` then `pass` | `except (X, Y) as _e:` then `log.warning(...)` | Python 3 syntax |

## Batch Fix Script (Full Pipeline)

The most reliable approach for 50+ files in a project:

```python
import re
from pathlib import Path

proj = Path(".")
for py_file in proj.glob("*.py"):
    if py_file.name.endswith(".bak"):
        continue
    content = py_file.read_text(encoding="utf-8", errors="replace")

    # Step 1: Fix "except X: as _var:" → "except X as _var:" 
    content = re.sub(
        r'(except[^:]*?):\s+as\s+(_\w+):',
        r'\1 as \2:',
        content
    )

    # Step 2: Fix bare "except: as _var:" → "except Exception as _var:"
    content = re.sub(
        r'^(\s*)except:\s+as\s+(_\w+):',
        r'\1except Exception as \2:',
        content,
        flags=re.MULTILINE
    )

    # Step 3: Fix indentation after except blocks
    lines = content.split("\n")
    modified = False
    for i in range(len(lines)):
        s = lines[i].strip()
        if "except" in s and " as _" in s and s.endswith(":"):
            indent = len(lines[i]) - len(lines[i].lstrip())
            expected = indent + 4
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and lines[j].strip():
                actual = len(lines[j]) - len(lines[j].lstrip())
                if actual < expected:
                    lines[j] = " " * expected + lines[j].lstrip()
                    modified = True
    if modified:
        py_file.write_text("\n".join(lines), encoding="utf-8")
```

### Step 4: Verify ALL files compile

```python
ok = fail = 0
for py in sorted(Path(".").glob("*.py")):
    try:
        compile(py.read_text(encoding="utf-8"), py.name, "exec")
        ok += 1
    except SyntaxError as e:
        fail += 1
        print(f"ERROR {py.name}: {e}")
print(f"OK: {ok}  FAIL: {fail}")
```

## Pitfalls

- **Don't use bare `except:`** — catches KeyboardInterrupt, SystemExit too. Always `except Exception:`.
- **Complex except patterns** like `except (OSError, json.JSONDecodeError):` or `except sqlite3.OperationalError:` need the broader regex `(except[^:]*?)` to match dotted names and parenthesized tuples.
- **Always compile-verify after batch edits** — regex can create syntax errors.
- **Beware of `except Exception: as _var:`** (colon BEFORE `as`) or `except: as _var:` (bare except with `as`). Two distinct patterns to catch.
- **Check indentation carefully** — regex may leave the replacement line at wrong indent level. Fix with the indentation pass above.
- **50-100+ files may have the same broken pattern** — use batch approach, not individual patch calls.
- **Some `except: pass` is intentional** (optional imports) — add a comment instead of removing entirely.

## Full Verification

Run `compile()` on EVERY `.py` file after changes. A single syntax error means the project won't start. Fix all before declaring done.
