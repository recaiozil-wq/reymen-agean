---
skill_id: 235f693884b0
usage_count: 1
last_used: 2026-06-16
---
# What's available?
command -v comfy >/dev/null 2>&1 && echo "comfy-cli: installed"
curl -s http://127.0.0.1:8188/system_stats 2>/dev/null && echo "server: running"