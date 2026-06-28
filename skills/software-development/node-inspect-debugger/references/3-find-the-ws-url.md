---
skill_id: 8bf76ffe33de
usage_count: 1
last_used: 2026-06-16
---
# 3. Find the WS URL
curl -s http://127.0.0.1:9229/json/list | jq -r '.[0].webSocketDebuggerUrl'