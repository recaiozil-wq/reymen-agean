---
skill_id: 9f06d90dad4b
usage_count: 1
last_used: 2026-06-16
---
## Probes — Liveness, Readiness, Startup

Understanding when to use each probe is critical:

| Probe | Failure Action | Use For |
|-------|---------------|---------|
| `startupProbe` | Kills container if slow to start | Slow-starting apps (JVM, Python) |
| `livenessProbe` | Restarts container | Deadlock / hung process detection |
| `readinessProbe` | Removes from Service endpoints | Temporary unavailability (DB reconnect) |

```yaml