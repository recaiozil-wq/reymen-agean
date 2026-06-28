---
skill_id: e09245effc62
usage_count: 1
last_used: 2026-06-16
---
## Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Invalid or expired API token | Regenerate at id.atlassian.com |
| `403 Forbidden` | Token lacks project permissions | Check token scopes and project access |
| `404 Not Found` | Wrong ticket key or base URL | Verify `JIRA_URL` and ticket key |
| `spawn uvx ENOENT` | IDE cannot find `uvx` on PATH | Use full path (e.g., `~/.local/bin/uvx`) or set PATH in `~/.zprofile` |
| Connection timeout | Network/VPN issue | Check VPN connection and firewall rules |