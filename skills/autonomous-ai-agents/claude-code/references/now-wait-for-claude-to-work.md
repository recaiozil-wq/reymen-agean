---
skill_id: e63270b18334
usage_count: 1
last_used: 2026-06-16
---
# Now wait for Claude to work
terminal(command="sleep 15 && tmux capture-pane -t claude-work -p -S -60")
```

**Note:** After the first trust acceptance for a directory, the trust dialog won't appear again. Only the permissions dialog recurs each time you use `--dangerously-skip-permissions`.