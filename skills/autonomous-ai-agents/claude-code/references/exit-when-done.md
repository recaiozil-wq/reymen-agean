---
skill_id: e8a7842a32de
usage_count: 1
last_used: 2026-06-16
---
# Exit when done
terminal(command="tmux send-keys -t claude-work '/exit' Enter")
```

**When to use interactive mode:**
- Multi-turn iterative work (refactor → review → fix → test cycle)
- Tasks requiring human-in-the-loop decisions
- Exploratory coding sessions
- When you need to use Claude's slash commands (`/compact`, `/review`, `/model`)