---
name: autonomous-ai-agents_self-improvement_references_orphan-md-detection-patch
description: Orphan .md Detection — Sync Script Patch
title: "Autonomous Ai Agents Self Improvement References Orphan Md Detection Patch"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Orphan .md Detection — Sync Script Patch |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Orphan .md Detection — Sync Script Patch

## Problem
Sync script (`sync_skills_to_obsidian.py`) uses `rglob("SKILL.md")` to find skills.
Root-level `.md` files (not in a `*/SKILL.md` structure) are invisible to the sync.

## Patch Applied
Added orphan detection at line ~214:
```python
orphan_mds = [f for f in sorted(SKILLS_DIR.glob("*.md"))
              if f.name != "SKILL.md" and f.is_file()]
if orphan_mds:
    names = ", ".join(f.name for f in orphan_mds)
    print(f"[UYARI] Standalone .md bulundu (sync edilmiyor): {names}")
```

## Practical Impact
- During self-improvement runs, if the `[UYARI]` fires, the agent knows to convert those `.md` files to proper SKILL.md directories
- Root `.md` files that are intentionally NOT skills (DESCRIPTION.md, index notes) — rename them to `*.md.obsolete` or move them to a `_archive/` directory so they don't trigger the warning
