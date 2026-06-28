---
skill_id: 8c8b56b8d922
usage_count: 1
last_used: 2026-06-16
---
## Required Worktree and Branch Pattern

Never run Codex directly in a shared dirty checkout. Use a branch/worktree name that ties the lane to the Kanban task and keeps untrusted edits isolated.

Recommended variables:

```bash
TASK_ID="${HERMES_KANBAN_TASK:-t_manual}"
REPO="/path/to/repo"
BASE="$(git -C "$REPO" rev-parse --abbrev-ref HEAD)"
SAFE_TASK="$(printf '%s' "$TASK_ID" | tr -cd '[:alnum:]_-')"
BRANCH="codex/${SAFE_TASK}/$(date -u +%Y%m%d%H%M%S)"
WORKTREE="/tmp/${SAFE_TASK}-codex-lane"
```

Create the isolated lane:

```bash
git -C "$REPO" fetch --all --prune
git -C "$REPO" worktree add -b "$BRANCH" "$WORKTREE" "$BASE"
git -C "$WORKTREE" status --short --branch
```

If the current Kanban workspace is already an isolated git worktree created for this task, you may create a sibling Codex branch inside it only if `git status --short` is clean except for intentional ReYMeN edits. Otherwise create a separate temporary worktree and cherry-pick or copy accepted commits back after reconciliation.

Cleanup after reconciliation:

```bash
git -C "$REPO" worktree remove "$WORKTREE"
git -C "$REPO" branch -D "$BRANCH"  # only after accepted commits were copied/cherry-picked or intentionally rejected
```

Keep the worktree if it is needed as an artifact for review; record it in `codex_lane.artifacts` and mention it in the handoff.