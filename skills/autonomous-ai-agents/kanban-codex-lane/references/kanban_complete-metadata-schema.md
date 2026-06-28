---
skill_id: 1f724d6684be
usage_count: 1
last_used: 2026-06-16
---
## kanban_complete Metadata Schema

Include this object under `metadata.codex_lane` for every task where the lane was considered. If Codex was not used, set `used: false` and explain why in `rejected_reason` or a sibling `notes` field.

```json
{
  "codex_lane": {
    "used": true,
    "mode": "exec | goal | skipped",
    "worktree": "/absolute/path/to/codex/worktree",
    "branch": "codex/t_caa69668/20260508100000",
    "command": "codex exec --full-auto ...",
    "result": "accepted | rejected | partial | timed_out",
    "accepted_commits": ["<sha1>", "<sha2>"],
    "rejected_reason": "empty when fully accepted; otherwise concrete reason",
    "tests_run": [
      {"command": "scripts/run_tests.sh tests/tools/test_x.py", "exit_code": 0, "owner": "hermes"},
      {"command": "codex-reported: npm test", "exit_code": 0, "owner": "codex"}
    ],
    "artifacts": ["/absolute/path/to/log-or-patch"]
  }
}
```

For tasks that intentionally skip Codex:

```json
{
  "codex_lane": {
    "used": false,
    "mode": "skipped",
    "worktree": null,
    "branch": null,
    "command": null,
    "result": "rejected",
    "accepted_commits": [],
    "rejected_reason": "Direct ReYMeN edit was smaller and safer than spawning Codex.",
    "tests_run": [],
    "artifacts": []
  }
}
```