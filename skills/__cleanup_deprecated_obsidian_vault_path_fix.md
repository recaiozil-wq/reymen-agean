---
name: __cleanup_deprecated_obsidian_vault_path_fix
description: __cleanup_deprecated_obsidian_vault_path_fix skill'i
category: genel
version: 1.0.0
---

---
name: obsidian-vault-path-fix
description: "Use whenever reading, writing, or syncing anything to Obsidian. Contains correct vault path and sync rules so cached wrong paths are never used again."
title: "Obsidian Vault Path Fix"
version: 1.0

audience: maintainer
tags: [obsidian, system]
category: __cleanup_deprecated_obsidian_vault_path_fix---

# Obsidian Vault Path Fix

## Correct vault path

- Correct vault: `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault`
- Wrong vault: `C:\Users\marko\Documents\Obsidian Vault`

Always use the correct vault path for every Obsidian read/create/edit operation.

## Startup verification

Run first on ReYMeN open:

```
python C:\Users\marko\hermes-ai\venv\Scripts\python.exe -c "from pathlib import Path; v=Path(r'C:\Users\marko\OneDrive\Belgeler\Obsidian Vault'); print('[OK]' if v.exists() else '[HATA]', v)"
```

## Skill sync target

- Source of truth: `skills_list`
- Markdown note: `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\ReYMeN Skills Sync.md`
- Optional skill bundle dir: `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\obsidian_skill_all_tree_0`

## Permanent request

This is a permanent, durable request: sync full skill
