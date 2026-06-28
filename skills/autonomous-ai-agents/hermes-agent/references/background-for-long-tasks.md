---
skill_id: eb7754148c40
usage_count: 1
last_used: 2026-06-16
---
# Background for long tasks:
terminal(command="hermes chat -q 'Set up CI/CD for ~/myapp'", background=true)
```

### Interactive PTY Mode (via tmux)

ReYMeN uses prompt_toolkit, which requires a real terminal. Use tmux for interactive spawning:

```