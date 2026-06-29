---
name: autonomous-ai-agents_kanban-codex-lane_references_verification-checklist
description: Verification Checklist
title: "Autonomous Ai Agents Kanban Codex Lane References Verification Checklist"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Verification Checklist |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Verification Checklist

- [ ] Codex was skipped or started only after `command -v codex`, `codex --version`, and optional goals feature checks.
- [ ] Codex ran only in an isolated worktree/branch.
- [ ] Prompt included task scope, ownership rules, PMB safety constraints when applicable, and verification commands.
- [ ] Hermes reviewed `git diff` and safety-sensitive files.
- [ ] Hermes ran canonical tests independently.
- [ ] `kanban_complete.metadata.codex_lane` follows the schema above.
- [ ] Temporary processes and unnecessary worktrees were cleaned up.
