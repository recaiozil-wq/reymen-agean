
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Bulk Text Replace_References_Context Aware Rename |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Context-Aware Rename: Project Name Change with External References

When renaming a project identifier (e.g., "hermes" → "R>eYMeN"), not every occurrence should change. Some may reference an external project (Nous Research's Hermes Agent), be part of a file path, or be a CLI parameter name. Blind replacement breaks functionality.

## Workflow

### 1. Scan — Find ALL occurrences first

```bash
# Case-insensitive, exclude noise dirs
grep -rni -i "OLD_NAME" --include='*.py' --include='*.md' --include='*.json' \
  --include='*.bat' --include='*.yaml' --include='*.yml' --include='*.cfg' \
  --include='*.ini' --include='*.txt' --include='*.sh' --include='*.ps1' \
  --include='*.html' --include='*.js' --include='*.ts' \
  --exclude-dir=.git --exclude-dir=venv --exclude-dir=node_modules \
  --exclude-dir=__pycache__ \
  . 2>/dev/null | sort
```

### 2. Categorize into 3 buckets

**Bucket A — Project's own name → RENAME**
- Variable names, class names, function names
- Log messages, docstrings about this project
- Config keys that reference this project's identity
- File content that says "this project is called X"

**Bucket B — External project reference → SKIP**
- "Powered by Hermes Agent (Nous Research)"
- "Hermes Agent comparison / gap analysis"
- References to upstream dependencies (e.g., `hermes-agent` npm/PyPI package)
- Documentation explaining the project's relationship to an upstream

**Bucket C — Would break functionality → ADAPT**
- CLI parameter names (`%1`=="hermes"): changing breaks user muscle memory
- File paths (`.claude/settings.json` → `hermes_projesi/`): changing breaks MCP/IDE configs
- Batch script labels (`:hermes`): changing breaks `goto` targets
- GitHub repo references (`download hermes`): changing breaks `git clone`/`pip install`
- Directory names still physically present on disk

For Bucket C, use an **alternative naming** if the full replacement contains special characters:
- `R>eYMeN` → not safe in batch scripts (`>` = I/O redirection), **not safe in Windows filenames** (`>` is forbidden by the OS)
- `ReYMeN` → safe in batch scripts, paths, CLI parameters, and filenames
- `reyemen` → safe everywhere (all lowercase, no special chars)

**Windows filename forbidden characters:** `\ / : * ? " < > |` — none of these can appear in a filename. If the new name contains any of these, use an alternative (e.g., `R>eYMeN.bat` is impossible → use `ReYMeN.bat`).

**Windows is case-insensitive for filenames:** `ReYMeN.bat`, `reyemen.bat`, and `REYMEN.BAT` all refer to the same file. A rename from `reyemen.bat` → `ReYMeN.bat` does NOT break existing commands or scripts that reference the old lowercase name.

### 3.5 Import-Chain Check Before File Rename

Before renaming any module file (`.py`), verify nothing imports it:

```bash
grep -rn "import OLD_NAME\|from OLD_NAME\|from.*OLD_NAME_\|import.*OLD_NAME_" \
  --include="*.py" --exclude-dir=venv --exclude-dir=.git --exclude-dir=__pycache__ \
  . 2>/dev/null
```

- **Zero results** → safe to rename (no import chain to break)
- **Results found** → update all import statements first, or SKIP the rename

**Why:** Renaming a `.py` file breaks `import old_name` in other files. Unlike content replacement (handled by `find -exec perl`), file renaming uses `mv` and requires manual caller updates.

### 3.6 File-Rename Execution (not content replace)

When renaming actual files (not just text inside them):

```bash
# 1. Rename each file
mv old_name.py new_name.py

# 2. Update any callers (scripts, batch files, configs referencing the old path)
#    Use targeted patch, not bulk find-and-replace

# 3. Clean stale __pycache__ artifacts
find . -path "*/__pycache__/*" -name "*old_name*" -delete 2>/dev/null
```

**Pattern:** `find` to locate files → `mv` per file → `patch` to update callers → clean `__pycache__`.

### 3.7 Final Verification After All Changes

```bash
# Files with old name in project root (should be 0)
find . -maxdepth 4 -type f -iname "*OLD_NAME*" \
  ! -path "./.hermes/*" ! -path "./skills/*" ! -path "./venv/*" \
  ! -path "./.git/*" ! -path "./__pycache__/*" 2>/dev/null | sort
```

## 4. Show user the categorized breakdown

Present as a table:

```
| Bucket | Files | Changes | Action |
|--------|-------|---------|--------|
| A: Project name | 5 files | 7 changes | R>eYMeN |
| B: External ref | 8 files | 0 changes | SKIP |
| C: Would break | 3 files | 4 changes | ReYMeN (adapted) |
```

Get explicit approval per category before applying.

### 4. Apply changes per category

**Bucket A** — direct find-and-replace:

```bash
find . -name '*.py' -type f \
  -not -path '*/venv/*' -not -path '*/.git/*' \
  -exec perl -i -pe 's/\bhermes\b/R>eYMeN/gi' {} +
```

**Bucket C** — targeted patches per file (use `patch` tool, not bulk find):

```bash
# Example: batch script label and echo message
perl -i -pe 's/Hermes Multi-Service/ReYMeN Multi-Service/g' reyemen.bat
perl -i -pe 's/:hermes/:hermes_agent/g' reyemen.bat
```

### 5. Verify nothing broke

```bash
# No remaining occurrences of old name (in Bucket A scope)
grep -rln 'OLD_NAME' --include='*.py' [excludes] | wc -l
# Should be 0 for Bucket A files

# Test that Bucket C items still work
# - CLI param: `reyemen.bat hermes` still works
# - File paths: MCP config still resolves
# - Batch labels: `goto :hermes_agent` still works
```

## Example from Session

**Goal:** Rename "hermes" → "R>eYMeN" in `Reymen Proje/hermes_projesi/`

**Scan result:** 38 files with "hermes"

**Categorization:**
| Bucket | Files | Action |
|--------|-------|--------|
| A: hermes_config.json, reyemen.bat echoes | 5 | R>eYMeN / ReYMeN |
| B: CHANGELOG.md ("Hermes Agent karsilastirma"), REYMEN.md, TEKNIK_BRIFING.md | 8 | SKIP |
| C: `%1`=="hermes" param, `:hermes` label, MCP path, `download hermes` cmd | 4 | Keep "hermes" or use "ReYMeN" |

**Changes applied (file renames):**
- `hermes_config.json` → `reyemen_config.json`
- `reyemen.bat` → `ReYMeN.bat` (echo messages also updated: `Hermes Multi-Service` → `ReYMeN Multi-Service`)
- `hermes_bootstrap.py` → `ReYMeN_bootstrap.py`
- `hermes_cli.py` → `ReYMeN_cli.py`
- `hermes_constants.py` → `ReYMeN_constants.py`
- `hermes_logging.py` → `ReYMeN_logging.py`
- `hermes_state.py` → `ReYMeN_state.py`
- `hermes_time.py` → `ReYMeN_time.py`
- `agent/transports/hermes_tools_mcp_server.py` → `agent/transports/ReYMeN_tools_mcp_server.py`
- `HERMES_GAP_ANALIZI.md` → `ReYMeN_GAP_ANALIZI.md`

**Internal reference updates:**
- `ReYMeN.bat`: `python hermes_cli.py %*` → `python ReYMeN_cli.py %*` (caller update after file rename)
- `ReYMeN.bat`: `:hermes` → `:hermes_agent` label + `goto :hermes` → `goto :hermes_agent`
- `ReYMeN.bat`: echo messages `reyemen.bat` → `ReYMeN.bat` (visual consistency)

**Cleanup:**
- `__pycache__/` deleted stale `.pyc` files with old names

**Preserved:**
- `%1`=="hermes" — CLI parameter still works with `reyemen.bat hermes`
- `hermes_cli.py` — file not renamed (still calls Hermes Agent)
- `.claude/settings.json` — path unchanged (MCP still works)
- `download hermes` — GitHub repo reference unchanged

## Windows-Specific Pitfalls

1. **`__pycache__` stale `.pyc` files:** After renaming `.py` files, the old `.pyc` files in `__pycache__/` persist with the old name. They don't cause errors (Python recompiles on import miss), but a `find -iname "*old_name*"` scan will still show them. Clean with `find . -path "*/__pycache__/*" -name "*old_name*" -delete`.
2. **`>` in batch files:** `echo R>eYMeN` writes `R` to file, not `>eYMeN` — `>` is I/O redirection. Use `echo ReYMeN` or escape with `R^>eYMeN` in batch context.
3. **`>` in Windows filenames is FORBIDDEN:** The `>` character (along with `\ / : * ? " < |`) cannot appear in any Windows file or directory name. Always use an alternative (e.g., `ReYMeN` instead of `R>eYMeN`).
4. **Windows case-insensitive filesystem:** `ReYMeN.bat`, `reyemen.bat`, and `REYMEN.BAT` all resolve to the same file. Renaming for visual consistency (lowercase → PascalCase) does NOT break existing commands.
5. **Path separators:** Do NOT change directory names in VS Code/IDE config files (`.vscode/settings.json`, `.claude/settings.json`) — they're absolute paths on the user's machine.
6. **`goto` labels:** In batch files, changing a `:label` requires also changing every `goto :label` that references it.
