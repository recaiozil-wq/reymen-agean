---
skill_id: 12a4cf30661d
usage_count: 1
last_used: 2026-06-16
---
# Task 2: Write tests
terminal(command="tmux new-session -d -s task2 -x 140 -y 40 && tmux send-keys -t task2 'cd ~/project && claude -p \"Write integration tests for the API endpoints\" --allowedTools \"Read,Write,Bash\" --max-turns 15' Enter")