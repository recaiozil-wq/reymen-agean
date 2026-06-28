---
skill_id: a36582055cda
usage_count: 1
last_used: 2026-06-16
---
# Monitor all
terminal(command="sleep 30 && for s in task1 task2 task3; do echo '=== '$s' ==='; tmux capture-pane -t $s -p -S -5 2>/dev/null; done")
```