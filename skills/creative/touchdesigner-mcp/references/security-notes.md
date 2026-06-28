---
skill_id: 173f8b28bf92
usage_count: 1
last_used: 2026-06-16
---
## Security Notes

- MCP runs on localhost only (port 40404). No authentication — any local process can send commands.
- `td_execute_python` has unrestricted access to the TD Python environment and filesystem as the TD process user.
- `setup.sh` downloads twozero.tox from the official 404zero.com URL. Verify the download if concerned.
- The skill never sends data outside localhost. All MCP communication is local.