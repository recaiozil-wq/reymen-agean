---
skill_id: e5c7c54673fb
usage_count: 1
last_used: 2026-06-16
---
# ~/.config/systemd/user/agentic-daily-sync.service
[Unit]
Description=Agentic OS Daily Sync

[Service]
Type=oneshot
ExecStart=/usr/local/bin/claude --cwd /path/to/project --command /daily-sync
```

```ini