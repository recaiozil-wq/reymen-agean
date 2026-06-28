# Codebase Hardening — Silent Except Fix & Dead File Cleanup

## When to Use

- A Python codebase has many `except: pass` blocks that silently swallow errors
- The project root is cluttered with test artifacts, logs, backups, and temporary files
- You need to harden a codebase before shipping or before deeper refactoring

---

## 1. Silent Except Census & Batch Fix

### Detection

Find every silent `except X: \n    pass` pattern across the project:

```python
from pathlib import Path
proje = Path("path/to/project")

silent = 0
for py_file in sorted(proje.glob("*.py")):
    content = py_file.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("except") and i < len(lines):
            next_line = lines[i].strip() if i < len(lines) else ""
            if next_line == "pass":
                silent += 1

print(f"Sessiz pass blok: {silent}")
```

### Batch Fix Script

Replace all `except X: \n    pass` blocks with logged versions. The script:

1. Scans every `.py` file in the project root
2. Detects if the file already uses `_modul_uyar()` for logging
3. Falls back to `print()` if no logging function exists
4. Skips files that already use `as _e` bindings on their except clauses
5. Writes the patched content back

```python
from pathlib import Path

proje = Path("path/to/project")
files_fixed = 0
total_fixed = 0

for py_file in sorted(proje.glob("*.py")):
    content = py_file.read_text(encoding="utf-8", errors="replace")
    lines = content.split("\n")
    modified = False
    has_modul_uyar = "_modul_uyar" in content

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith("except") and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line == "pass" and " as " not in stripped:
                short_name = py_file.stem.replace("-", "_")[:8]
                if has_modul_uyar:
                    new_lines.append(
                        f"{line.rstrip()} as _{short_name}_e{i}:"
                    )
                    new_lines.append(
                        f"    _modul_uyar(\"{py_file.name}:{i+1}\", _{short_name}_e{i})"
                    )
                else:
                    new_lines.append(
                        f"{line.rstrip()} as _{short_name}_e{i}:"
                    )
                    new_lines.append(
                        f"    print(f\"[UYARI] {py_file.name}:{i+1} - {{_{short_name}_e{i}}}\")"
                    )
                modified = True
                total_fixed += 1
                i += 2  # skip original pass line
                continue
        new_lines.append(line)
        i += 1

    if modified:
        py_file.write_text("\n".join(new_lines), encoding="utf-8")
        files_fixed += 1

print(f"✅ Düzeltilen dosya: {files_fixed}")
print(f"✅ Düzeltilen blok: {total_fixed}")
```

### Verification

After fixing, confirm zero silent blocks remain:

```python
total_remaining = 0
for py_file in sorted(proje.glob("*.py")):
    content = py_file.read_text(encoding="utf-8")
    lines = content.split("\n")
    count = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("except") and i < len(lines):
            if lines[i].strip() == "pass":
                count += 1
    if count > 0:
        print(f"  {py_file.name}: {count} blok kaldı")
    total_remaining += count
print(f"Kalan sessiz pass blok: {total_remaining}")
```

### Manual Steps (for complex cases)

Some except blocks can't be batch-fixed because:
- They're nested in complex control flow
- They don't have a clean `pass` on the next line (e.g., `except Exception: pass` on one line)
- The `_modul_uyar` import isn't available in the function scope

For these, use `patch()` with enough context to be unique:

```python
# Before:
except Exception:
    pass

# After:
except Exception as _hata_adi:
    _modul_uyar("Modül adı:bağlam", _hata_adi)
```

### What to Look For in main.py (Entry Points)

Entry point files (`main.py`, `cli.py`, `app.py`) tend to accumulate the most:

| Pattern | Meaning |
|---------|---------|
| `try: import X` / `except: pass` | Optional module — log the failure |
| `except Exception: pass` in hot path | Runtime errors hidden — almost always a bug |
| `except ImportError: pass` | Graceful optional dep — add a comment explaining why it's optional |

---

## 2. Dead File Identification & Cleanup

### Categorization

Files to move to a backup folder typically fall into these categories:

| Category | Examples | Signal |
|----------|----------|--------|
| **Test artifacts** (scattered) | `test_*.py`, `*_test.py` in root | Duplicate of organized `tests/` dir |
| **Backup/duplicate modules** | `*_backup.py`, `*_patch.py`, `*.bak` | Same class name exists in another file |
| **Log files** | `*.log`, `cua_log.txt`, `bridge.log` | Runtime artifacts, not source |
| **Old reports** | `ANALIZ_RAPORU.md`, `PLAN.md`, `REVIEW.md` | Session docs, not project docs |
| **Build configs** | `Dockerfile`, `Makefile`, `flake.nix` | Only if project doesn't use them |
| **Temp/cache** | `.coverage`, `.pytest_cache`, `skill_usage.json` | Generated, can be regenerated |
| **One-off scripts** | `setup_keys.py`, `build_exe.py`, `web_ui.py` | Run-once utilities |

### Cleanup Workflow

```python
import shutil
from pathlib import Path

proje = Path("path/to/project")
hedef = Path("path/to/backup/folder")
hedef.mkdir(parents=True, exist_ok=True)

dead_files = [
    # List files to move here
]

moved = []
for f in dead_files:
    src = proje / f
    if src.exists() and src.is_file():
        shutil.move(str(src), str(hedef / f))
        moved.append(f)

print(f"✅ Taşınan: {len(moved)} dosya ({sum((hedef/f).stat().st_size for f in moved):,} bytes)")
```

### Pre-Move Checklist

Before moving a file, check:

- [ ] Is it imported anywhere in the codebase? (`grep -r "import " | grep fileName`)
- [ ] Is it referenced in a config, docs, or README?
- [ ] Is it a required dependency for another module?
- [ ] Is it part of a test suite the user relies on?

If any answer is "yes" → keep it or investigate further before moving.

---

## 3. Critical Distinctions

### `except: pass` vs Graceful Degradation

Not all silent catches are bad. Legitimate patterns:

**Acceptable:** Optional dependency with fallback
```python
try:
    import orjson
except ImportError:
    import json as orjson  # ✅ Graceful fallback, no error hidden
```

**Bad:** Generic exception swallowed
```python
try:
    self.aktif_hafiza_plugin.tur_senkronize(mesajlar)
except Exception:
    pass  # ❌ What error? Plugin broken? Network down? We'll never know
```

**Fixed:**
```python
try:
    self.aktif_hafiza_plugin.tur_senkronize(mesajlar)
except Exception as e:
    _modul_uyar("Hafıza plugin tur_senkronize", e)  # ✅ Error visible, system continues
```

### Module Import Strategy

For optional modules, use a consistent pattern across the codebase:

```python
try:
    import optional_module
    _OPTIONAL_MODULE = optional_module
except ImportError as e:
    _modul_uyar("optional_module", e, "özellik devre dışı")
    _OPTIONAL_MODULE = None
```

Not:
```python
try:
    import optional_module
    _OPTIONAL_MODULE = optional_module
except Exception:
    pass  # ❌ Hides both ImportError AND AttributeError AND ...
```

---

## Pitfalls

1. **Batch script may break files with unusual indentation** — Always run compilation check (`ast.parse`) after batch fix
2. **Some `except: pass` blocks are intentional loop control** — `except StopIteration: pass` in generator code is valid. Only replace when the exception type is broad (Exception, bare `except:`)
3. **`_modul_uyar` may not exist in all scopes** — Batch script falls back to `print()` for files without it, but manually check that `print()` output reaches the user (not redirected to /dev/null)
4. **Dead files may be referenced in non-Python configs** — Always grep for the filename across the whole project before moving
5. **One-line `except: pass`** — Pattern `except: pass` on a single line won't be caught by the newline-based scanner. Handle these manually or with a separate regex pass
