---
name: software-development-error-handling-audit
description: 'Systematically scan, identify, and fix silent error-handling patterns
  (`except: pass`, bare `except Exception:`) in Python codebases. Also covers dead-file
  removal and duplicate-module resolution.'
title: Software Development Error Handling Audit
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

and duplicate files across a Python codebase. Batch-fix try/except pass, duplicate
  modules, and temp artifacts.
# Error Handling Audit — Systematic Codebase Cleanup

Systematically scan, identify, and fix silent error-handling patterns (`except: pass`, bare `except Exception:`) in Python codebases. Also covers dead-file removal and duplicate-module resolution.

## When to Use

- User asks to "fix silent errors", "temizle ölü dosyaları", or "try/except'leri düzelt"
- Codebase has many `except Exception: pass` or `except ImportError: pass` blocks
- Duplicate files exist in root and subdirectory (e.g., root + `agent/`)
- Temporary/test/backup files are mixed with production code
- Python files have syntax errors from batch-find-and-replace operations

## Workflow

### Phase 1 — Scan for Silent Exceptions

```python
from pathlib import Path

proje = Path("<project-path>")

for py_file in sorted(proje.glob("*.py")):
    content = py_file.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("except") and i < len(lines):
            next_line = lines[i].strip()
            if next_line == "pass":
                # Found silent except — needs fixing
```

### Phase 2 — Batch Fix Silent Exceptions

**Pattern 1 — `except Exception: pass` → logged:**

```python
# BEFORE
except Exception:
    pass

# AFTER (file has _modul_uyar):
except Exception as _module_e123:
    _modul_uyar("module.py:context", _module_e123)

# AFTER (no _modul_uyar):
except Exception as _module_e123:
    print(f"[UYARI] module.py:123 - {_module_e123}")
```

**Pattern 2 — `except ImportError: pass`:**

```python
# BEFORE
except ImportError:
    pass

# AFTER
except ImportError:
    _modul_uyar("module_name", "kütüphane eksik, alternatif kullanılacak")
```

**Pattern 3 — Syntax corruption `except Exception: as _var:`:**

The regex `r'except (\w+(?:\([^)]*\))?):\s+as\s+(_\w+):'` doesn't catch all patterns. Use this comprehensive fix:

```python
import re
content = re.sub(
    r'(except[^:]*?):\s+as\s+(_\w+):',
    r'\1 as \2:',
    content
)
```

Then fix indentation of the line after every `except ... as _var:`:

```python
indent_level = len(lines[i]) - len(lines[i].lstrip())
expected = indent_level + 4
# Fix next non-empty line if under-indented
```

### Phase 3 — Batch Fix Indentation After Auto-Fix

After regex replacement, the next line after `except` often has wrong indentation (e.g., print at column 0 instead of under the except block). Fix with:

```python
j = i + 1
while j < len(lines) and lines[j].strip() == "":
    j += 1
if j < len(lines) and lines[j].strip():
    actual = len(lines[j]) - len(lines[j].lstrip())
    if actual < expected:
        lines[j] = " " * expected + lines[j].lstrip()
```

### Phase 4 — Verify Syntax

Always compile-fix after batch operations:

```python
try:
    compile(content, py_file.name, "exec")
    print(f"✅ OK")
except SyntaxError as e:
    print(f"❌ {e}")
```

### Phase 5 — Remove Dead Files

Identify temp/backup/duplicate files with pattern matching:

| Category | Patterns |
|----------|----------|
| Test artifacts | `test_*.py`, `*_test.py`, `motor_test.py`, `son_test.py`, `react_test.py` |
| Backup files | `*.bak`, `*backup*`, `*_backup.py`, `*.zip` (beyin.zip, motor.zip) |
| Duplicate modules | Same filename in root + subdir (keep the one that's imported) |
| Logs | `*.log` files |
| Temporary | `.coverage`, `_test_*`, `_key.*`, `_progress*.txt` |
| Cache | `.skills_prompt_snapshot.json`, `skill_usage.json` |

### Phase 6 — Resolve Duplicate Files

When files exist in both root and a subdirectory (e.g., `agent/`):

1. Check which version is actually imported (scan import statements)
2. Move unused duplicates to `ReYMeN_ölü_dosyalar/<category>/`
3. For used duplicates, list them as known "overrides" in sync scripts

## Pitfalls

1. **Don't use bare `except:`** — catches `KeyboardInterrupt` and `SystemExit`. Always use `except Exception:` when catching general errors.
2. **Regex can corrupt syntax** — `except Exception: as _var:` is invalid Python. The regex `r'(except[^:]*?):\s+as\s+(_\w+):'` catches `except X: as _var:` but misses `except (A, B): as _var:` and bare `except: as _var:`. Use the comprehensive fix from Phase 2.
3. **Don't silently remove files** — move to a `ReYMeN_ölü_dosyalar/` folder instead of deleting, in case something is needed later.
4. **Always verify import chains** — a "duplicate" file in root might actually be the active version while the subdir copy is a reference backup.
5. **Heritage modules** — `agent/` dir files often import from `agent.` prefix, root files import bare. The import path determines which version is live.

## Verification

After cleanup:
```bash
# Count remaining silent passes
grep -r "except.*:\s*$" *.py | grep -A1 "except" | grep "pass" | wc -l

# Verify all Python files compile
python -c "
from pathlib import Path
ok = fail = 0
for f in Path('.').glob('*.py'):
    try:
        compile(f.read_text(), f.name, 'exec'); ok+=1
    except SyntaxError: fail+=1
print(f'OK:{ok} FAIL:{fail}')
"

# Check for remaining duplicates
for f in agent/*.py; do
    fn=$(basename "$f")
    [ -f "$fn" ] && echo "DUPLICATE: $fn"
done
```
