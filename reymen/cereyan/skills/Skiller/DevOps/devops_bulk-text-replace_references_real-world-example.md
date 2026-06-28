
> **Kategori:** DevOps

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Devops_Bulk Text Replace_References_Real World Example |
| **Nerede?** | DevOps/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Real-World Example: hermes → R>eYMeN across 2,845 files

This was a session where the user wanted to rename "hermes" to "R>eYMeN" in all Python files of a large project (~2,845 .py files, 1,629 initially containing the target).

## Approach Timeline

### Attempt 1: Batch loop with absolute paths ❌

```python
# This DID NOT work reliably
for f in files:
    terminal(f"perl -i -pe 's/\\bhermes\\b/R>eYMeN/gi' '{proj}/{f}'")
```

Files with spaces in path segments or special characters were silently skipped. After the loop, `grep -rln` still showed 1,000+ remaining files.

### Attempt 2: find inside loop with cd ❌

```python
# Better but still missed files
for f in files:
    terminal(f"cd '{proj}' && perl -i -pe 's/\\bhermes\\b/R>eYMeN/gi' '{f}'")
```

The `find .` inside the `cd` found fewer files (1,235 vs 2,845) because the `find` command was piped through terminal which has a 50KB output cap.

### Attempt 3: find -exec perl ✅ (SOLUTION)

```bash
cd '/c/Users/marko/OneDrive/Desktop/Reymen Proje/hermes_projesi'
find . -name '*.py' -type f \
  -not -path '*/venv/*' -not -path '*/node_modules/*' \
  -not -path '*/.git/*' -not -path '*/__pycache__/*' \
  -exec perl -i -pe 's/\bhermes\b/R>eYMeN/gi' {} +
```

Exit code 0, zero remaining files after verification.

## Word Boundary vs Substring

**First pass** (word boundary `\bhermes\b`): 8,355 replacements across 1,048 files.
- Missed: `hermes_pkce`, `hermes_cli`, `.hermes/skills`, `hermes_output`
- Safe for imports — `import hermes_cli.xxx` stayed unchanged

**Second pass** (plain `s/hermes/R>eYMeN/gi`): 28,762 replacements.
- Caught everything including compound words
- Broke imports: `import hermes_cli.xxx` → `import R>eYMeN_cli.xxx` (directory still `hermes_cli/`)
- User was warned and accepted the risk

## Key Numbers

| Metric | Value |
|--------|-------|
| Total .py files | ~2,845 |
| Initial files with target | 1,629 |
| Word boundary replacements | 8,355 |
| Full substring replacements | 28,762 |
| Backup size | 1,048 files |
| Final remaining "hermes" | 0 |

## Windows Quirks Encountered

- `du -sh .` timed out after 180s — project too large for immediate size check
- `find` from absolute path `/c/Users/...` found 2,845 files, but `find .` from within `cd` found only 1,235 — due to terminal output 50KB cap
- `grep -rln 'pattern' | wc -l` reliable for counting
- Backup: `cp` with path creation via `mkdir -p` worked on git-bash
