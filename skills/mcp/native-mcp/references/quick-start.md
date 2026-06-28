---
skill_id: a96216a022e6
usage_count: 1
last_used: 2026-06-16
---
## Quick Start

Add MCP servers to `~/.hermes/config.yaml` under the `mcp_servers` key:

```yaml
mcp_servers:
  time:
    command: "uvx"
    args: ["mcp-server-time"]
```

Restart ReYMeN Agent. On startup it will:
1. Connect to the server
2. Discover available tools
3. Register them with the prefix `mcp_time_*`
4. Inject them into all platform toolsets

You can then use the tools naturally -- just ask the agent to get the current time.