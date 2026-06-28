---
skill_id: 97a673bc1895
usage_count: 1
last_used: 2026-06-16
---
## When to Use

Use the Codex lane when all of these are true:

- The Kanban task is a coding, refactor, documentation, test, or mechanical migration task with clear acceptance criteria.
- A bounded diff can be evaluated by ReYMeN in one run.
- The repo can be copied or checked out in an isolated git worktree/branch.
- ReYMeN can run the relevant tests itself after Codex exits.
- The prompt can state all safety constraints and files that must not change.

Do not use the Codex lane when any of these are true:

- The task requires human judgment that is not already captured in the Kanban body.
- The worker lacks repo access, Codex auth, or time to reconcile the result.
- The change touches secrets, credential stores, private user data, or production order-entry systems.
- A small direct edit is faster and safer than spawning another agent.
- The task is research-only and should produce a written handoff rather than a diff.
- The worker would be tempted to mark Done based only on Codex self-report.