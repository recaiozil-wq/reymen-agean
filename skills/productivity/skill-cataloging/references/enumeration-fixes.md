---
skill_id: 2e94b7214a69
usage_count: 1
last_used: 2026-06-16
---
# Enumeration Fixes for Skill Cataloging

## Why `skills_list` + `skill_view` bulk copy fails

- `skills_list` returns only ~20 base skills. Sub-skills are omitted.
- `skill_view` returns a JSON wrapper with pre-rendered content and truncates at ~32K chars. It also cannot `exec()` `skill_view(name='a/b')` reliably for nested skills.
- The correct method is filesystem enumeration under `~/.hermes/skills` + direct copy of raw SKILL.md.

## Windows path helpers

Resolve vault path from `OBSIDIAN_VAULT_PATH` env var or fallback `C:\Users\<user>\Documents\Obsidian Vault`.
Quote paths with spaces or translate to MSYS short paths.

## Copied counts by platform

Run this after copies to verify:

```bash
echo "Copied: $(find TARGET_DIR -name SKILL.md | wc -l)"
```

## Obsidian vault vs ReYMeN skills relationship

The vault's `ReYMeN/Skills/` directory is a **mirrored copy** of the ReYMeN agent's skill repository (`~/.hermes/skills/`). Both contain the same skills with the same structure (categories, subdirectories, SKILL.md files). The Obsidian copy exists for offline browsing and reference — it is NOT the canonical source.

When scanning the vault for skills:
- Use `mcp_filesystem_directory_tree` on `ReYMeN/Skills/` to get the full tree (it reveals ALL subdirectories that `mcp_filesystem_search_files` with `**/*.md` may miss)
- Each `.md` file is a skill note — categories map directly to ReYMeN skill categories
- To **use** a skill (load/execute), always call `skill_view(name)` — the Obsidian copy is read-only reference
- The vault copy may be slightly outdated vs the live ReYMeN skill store if the user hasn't synced recently

## File scanning quirks on Windows

- `mcp_filesystem_search_files` with pattern `**/*.md` may NOT return files inside deeply nested subdirectories. Always use `directory_tree` first to learn the full shape, then read individual files.
- Files in `ReYMeN/Skills/` are real .md skill notes (not ReYMeN agent SKILL.md files) — they contain human-readable descriptions and usage notes, not formal frontmatter. They document what the agent's skills DO, not the agent's executable skill code.
- For bulk vault scanning across a large skill tree (140+ files), use `delegate_task` with parallel tasks (max 3 concurrent children) and file-read tools within each child. Each child should scan a subset of categories.
