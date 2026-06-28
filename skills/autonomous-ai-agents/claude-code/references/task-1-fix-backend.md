---
skill_id: 2344a9585f6f
usage_count: 1
last_used: 2026-06-16
---
# Task 1: Fix backend
terminal(command="tmux new-session -d -s task1 -x 140 -y 40 && tmux send-keys -t task1 'cd ~/project && claude -p \"Fix the auth bug in src/auth.py\" --allowedTools \"Read,Edit\" --max-turns 10' Enter")