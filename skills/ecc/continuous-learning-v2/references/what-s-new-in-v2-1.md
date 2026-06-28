---
skill_id: 76d7270b99fe
usage_count: 1
last_used: 2026-06-16
---
## What's New in v2.1

| Feature | v2.0 | v2.1 |
|---------|------|------|
| Storage | Global (`~/.claude/homunculus/`) | Project-scoped (`${XDG_DATA_HOME:-~/.local/share}/ecc-homunculus/projects/<hash>/`) |
| Scope | All instincts apply everywhere | Project-scoped + global |
| Detection | None | git remote URL / repo path |
| Promotion | N/A | Project → global when seen in 2+ projects |
| Commands | 4 (status/evolve/export/import) | 6 (+promote/projects) |
| Cross-project | Contamination risk | Isolated by default |