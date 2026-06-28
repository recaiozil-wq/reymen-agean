---
skill_id: bee0e2cc68de
usage_count: 1
last_used: 2026-06-16
---
## Monitoring, Timeout, and Kill Behavior

Start long Codex lanes in the background with PTY and completion notification:

```python
result = terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
session_id = result["session_id"]
```

Monitor without interfering:

```python
process(action="poll", session_id=session_id)
process(action="log", session_id=session_id, limit=200)
process(action="wait", session_id=session_id, timeout=300)
```

Send a Kanban heartbeat every few minutes for lanes longer than two minutes, e.g. `kanban_heartbeat(note="Codex lane running in <WORKTREE>; waiting for tests/diff")`.

Kill conditions:

- No useful output for the task's remaining runtime budget.
- Codex requests secrets, production credentials, or external permissions.
- Codex attempts to modify files outside the worktree.
- Codex starts unrelated rewrites or dependency churn.
- Codex is still running near the worker timeout and no safe partial artifact exists.

Kill command:

```python
process(action="kill", session_id=session_id)
```

After kill, inspect `git status --short`, preserve useful patches only if safe, and record `codex_lane.result: timed_out` or `rejected` with a concrete `rejected_reason`.