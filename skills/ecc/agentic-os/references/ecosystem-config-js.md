---
skill_id: 79f9fd43ee2d
usage_count: 1
last_used: 2026-06-16
---
# ecosystem.config.js
module.exports = {
  apps: [{
    name: 'agentic-daily-sync',
    script: 'claude',
    args: '--cwd /path/to/project --command /daily-sync',
    cron_restart: '0 8 * * *',
    autorestart: false
  }]
};
```