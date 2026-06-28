---
skill_id: e5bd7f4fcbd8
usage_count: 1
last_used: 2026-06-16
---
## Setup (Automated)

Run the setup script to handle everything:

```bash
bash "${REYMEN_HOME_PATH:-$HOME/.hermes}/skills/creative/touchdesigner-mcp/scripts/setup.sh"
```

The script will:
1. Check if TD is running
2. Download twozero.tox if not already cached
3. Add `twozero_td` MCP server to ReYMeN config (if missing)
4. Test the MCP connection on port 40404
5. Report what manual steps remain (drag .tox into TD, enable MCP toggle)

### Manual steps (one-time, cannot be automated)

1. **Drag `~/Downloads/twozero.tox` into the TD network editor** → click Install
2. **Enable MCP:** click twozero icon → Settings → mcp → "auto start MCP" → Yes
3. **Restart ReYMeN session** to pick up the new MCP server

After setup, verify:
```bash
nc -z 127.0.0.1 40404 && echo "twozero MCP: READY"
```