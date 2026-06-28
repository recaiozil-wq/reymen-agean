---
skill_id: 993025ed5c09
usage_count: 1
last_used: 2026-06-16
---
# Streamlit Access Control (IP Restriction)

Streamlit **removed** `--server.allowIps` / `--server.denyIps` flags in version 1.58.0+.

## What happened

```
$ streamlit run app.py --server.allowIps=178.233.208.119
Error: No such option '--server.allowIps'. (Did you mean one of:
'--server.allowRunOnSave', '--server.headless', '--server.port'?)
```

The `allowIps`/`denyIps` flags existed in older versions but were removed. The help output no longer lists them.

## Current state (Streamlit 1.58.0)

| Feature | Status |
|---------|--------|
| `--server.allowIps` | **Removed** |
| `--server.denyIps` | **Removed** |
| `--server.address=0.0.0.0` | Works — opens to ALL interfaces |
| `--server.address=127.0.0.1` | Default — localhost only |
| `--client.allowedOrigins` | Exists — for iframe embedding, NOT IP filtering |

## What to use instead

### Scenario 1: Single-user on same machine (recommended)
Just run without `--server.address`. Default localhost-only binding is secure.

```bash
C:/Users/marko/hermes-ai/venv/Scripts/python.exe -m streamlit run app.py \
  --server.port=8501 --server.headless=true
```
Access: `http://localhost:8501`

### Scenario 2: Need same-network access but IP-restricted
No built-in Streamlit solution. Options:

**Option A — Windows Firewall rule:**
```powershell
New-NetFirewallRule -DisplayName "Streamlit Allow 178.233.208.119" `
  -Direction Inbound -Protocol TCP -LocalPort 8501 `
  -RemoteAddress 178.233.208.119 -Action Allow
```

**Option B — Reverse proxy (nginx/Caddy):**
Run streamlit on localhost:8501, proxy through nginx with `allow/deny` directives.

### Scenario 3: Open to all (not recommended)
```bash
... --server.address=0.0.0.0
```
⚠️ Anyone on the network can access.
