---
skill_id: dbf513b91646
usage_count: 1
last_used: 2026-06-16
---
# Wait for startup, then send a message
terminal(command="sleep 8 && tmux send-keys -t agent1 'Build a FastAPI auth service' Enter", timeout=15)