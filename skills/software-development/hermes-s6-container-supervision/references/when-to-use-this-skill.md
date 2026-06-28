---
skill_id: 00ea2ef764b6
usage_count: 1
last_used: 2026-06-16
---
## When to use this skill

Load this skill when you're working on:
- Adding or removing a static service in the ReYMeN Docker image (something that should be supervised at every container start, like the dashboard)
- Diagnosing why a per-profile gateway isn't starting, restarting, or surviving `docker restart`
- Understanding why the container's CMD is `/opt/hermes/docker/main-wrapper.sh` and how leading-dash args reach the user's program
- Modifying `cont-init.d` boot scripts (UID remap, volume seeding, profile reconciliation)
- Changing the rendered run-script for per-profile gateways (Phase 4)

If you're just running the ReYMeN Agent and want to use Docker, see `website/docs/user-guide/docker.md` instead.