---
skill_id: efe79c321127
usage_count: 1
last_used: 2026-06-16
---
## Architecture

```
ReYMeN Agent -> MCP (Streamable HTTP) -> twozero.tox (port 40404) -> TD Python
```

36 native tools. Free plugin (no payment/license — confirmed April 2026).
Context-aware (knows selected OP, current network).
Hub health check: `GET http://localhost:40404/mcp` returns JSON with instance PID, project name, TD version.