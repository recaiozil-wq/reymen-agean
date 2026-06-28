---
skill_id: a53aecbcdae7
usage_count: 1
last_used: 2026-06-16
---
## Mode Selection

Use `codex exec` for bounded one-shot edits where Codex should exit on its own:

```python
terminal(
    command="codex exec --full-auto '$(cat /tmp/codex_prompt.md)'",
    workdir=WORKTREE,
    background=True,
    pty=True,
    notify_on_complete=True,
)
```

Use Codex `/goal` only for broader multi-step work that benefits from durable objective tracking. Launch interactively in a PTY/tmux session or with `codex --enable goals` if the feature is disabled by default. Keep the goal objective self-contained: repo path, task id, safety constraints, allowed scope, acceptance criteria, tests, and commit expectations.

Example `/goal` objective text to paste into Codex:

```text
/goal Work in this repository only: <WORKTREE>. Task: <TASK_ID> <TITLE>.
ReYMeN owns the Kanban lifecycle; do not call ReYMeN kanban tools or messaging.
Create small commits on branch <BRANCH>. Follow the PMB safety constraints in the prompt.
Run the requested verification commands and report exact outputs. Stop after producing a diff and summary.
```

Do not use `--yolo` for prediction-market-bot or safety-sensitive repos. Prefer `--full-auto` inside the isolated worktree, then rely on ReYMeN reconciliation.