---
skill_id: 864eb247f2af
usage_count: 1
last_used: 2026-06-16
---
## Verification Checklist

- [ ] Codex was skipped or started only after `command -v codex`, `codex --version`, and optional goals feature checks.
- [ ] Codex ran only in an isolated worktree/branch.
- [ ] Prompt included task scope, ownership rules, PMB safety constraints when applicable, and verification commands.
- [ ] ReYMeN reviewed `git diff` and safety-sensitive files.
- [ ] ReYMeN ran canonical tests independently.
- [ ] `kanban_complete.metadata.codex_lane` follows the schema above.
- [ ] Temporary processes and unnecessary worktrees were cleaned up.