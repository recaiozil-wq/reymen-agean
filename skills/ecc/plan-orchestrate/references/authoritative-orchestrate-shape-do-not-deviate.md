---
skill_id: 7543fcd155e8
usage_count: 1
last_used: 2026-06-16
---
## Authoritative `/orchestrate` shape (do not deviate)

```
{ORCH_CMD} custom "<agent1>,<agent2>,...,<agentN>" "<task description>"
```

Where `{ORCH_CMD}` is determined in Phase 0 (see below). The command string in the emitted output **always uses one concrete form** — never both, never a placeholder.

- `custom` is a sequential chain; each agent's HANDOFF feeds the next.
- Comma-separated agent list. No spaces preferred; one space tolerated.
- No `--mode` / `--gate` / `--agents=...` flags exist — never invent them.
- Agent names come from the catalogue in this skill. Embedded double quotes in the task description are escaped as `\"`.