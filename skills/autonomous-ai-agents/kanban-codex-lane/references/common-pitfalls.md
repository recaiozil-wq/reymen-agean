---
skill_id: 53cbf1a3890e
usage_count: 1
last_used: 2026-06-16
---
## Common Pitfalls

1. Treating Codex self-report as verification. Always inspect the diff and rerun tests from ReYMeN.
2. Running Codex in the user's dirty main checkout. Always isolate in a worktree/branch.
3. Letting Codex own Kanban. Codex may summarize progress, but ReYMeN writes board state.
4. Forgetting PMB safety invariants in the prompt. Missing safety text is a lane setup failure.
5. Using `/goal` for quick edits. Prefer `codex exec` unless durable multi-step continuation is needed.
6. Killing a stuck lane without recording why. `rejected_reason` must explain the decision.
7. Accepting broad unrelated cleanup because tests pass. Reject or cherry-pick only the scoped changes.