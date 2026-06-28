---
skill_id: 4b43c0999479
usage_count: 1
last_used: 2026-06-16
---
## Ownership Rules

1. ReYMeN owns the Kanban lifecycle. Codex must never call `kanban_complete`, `kanban_block`, `kanban_create`, gateway messaging, or any ReYMeN board CLI as a substitute for the worker.
2. ReYMeN owns final acceptance. Treat Codex commits/diffs as untrusted patches until reviewed and verified.
3. ReYMeN owns test execution. Codex may run tests, but those runs are advisory; repeat required verification from ReYMeN with the repo's canonical wrapper.
4. ReYMeN owns safety. If Codex changes safety boundaries, risk gates, live trading behavior, or secrets handling, reject the lane even if tests pass.
5. ReYMeN owns cleanup. Kill stuck Codex processes and remove temporary worktrees when they are no longer needed.