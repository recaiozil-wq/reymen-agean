---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

- [ ] `CLAUDE.md` is under 200 lines and fits in context window
- [ ] Each agent file is under 100 lines and focused on one domain
- [ ] `data/` is git-ignored for sensitive logs, git-tracked for decisions and specs
- [ ] Commands use imperative names: `/daily-sync`, not `/run-daily-sync`
- [ ] Logs are append-only; never edit past daily logs
- [ ] Every agent has a `Memory Scope` section defining what files it reads
- [ ] Reflections are written at the end of every session
- [ ] Scheduled tasks use external cron (LaunchAgent, systemd, pm2), not Claude Code's session cron
- [ ] Cost tracking: log API spend per session in `data/logs/<date>-costs.json`
- [ ] One project = one Agentic OS. Do not share a single `CLAUDE.md` across unrelated projects.