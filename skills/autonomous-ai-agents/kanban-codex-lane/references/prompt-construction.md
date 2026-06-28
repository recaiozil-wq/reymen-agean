---
skill_id: efa8932d6bdb
usage_count: 1
last_used: 2026-06-16
---
## Prompt Construction

Use the linked template at `templates/pmb-codex-lane-prompt.md` for prediction-market-bot work. For other repos, keep the same structure and replace the PMB-specific safety block with repo-specific invariants.

Every Codex prompt must include:

- `task_id`, title, and full Kanban acceptance criteria.
- Repo path, worktree path, branch name, and allowed file scope.
- Explicit statement: ReYMeN owns Kanban lifecycle; Codex is an input lane only.
- Required output: concise summary, files changed, commits, tests run, and known risks.
- Prohibited actions: secrets access, external messaging, board mutation, unrelated refactors, dependency upgrades unless required.
- Verification commands Codex may run and commands ReYMeN will run afterward.

For PMB, include these mandatory safety constraints verbatim:

```text
PMB safety constraints:
- live-SIM is paper-only; do not add or enable live REST order entry.
- Never use market orders.
- Do not add execution crossing or bypass price/risk checks.
- Do not fake passive fills, fills, PnL, order states, or reconciliation evidence.
- Do not weaken risk gates, limits, kill switches, or fail-closed behavior.
- Keep research/selection outside the C++ hot path unless explicitly requested.
- Do not read, print, write, or require secrets/tokens/credentials.
```