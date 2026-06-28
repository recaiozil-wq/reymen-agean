---
skill_id: 796d846781d8
usage_count: 1
last_used: 2026-06-16
---
# Resume with session ID
terminal(command="claude -p 'Continue and add connection pooling' --resume $(cat /tmp/session.json | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"session_id\"])') --max-turns 5", workdir="/project", timeout=120)