---
skill_id: 8e13c4cac14c
usage_count: 1
last_used: 2026-06-16
---
# ~/.config/systemd/user/agentic-daily-sync.timer
[Unit]
Description=Run daily sync every morning

[Timer]
OnCalendar=*-*-* 8:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Cross-Platform: pm2

```bash