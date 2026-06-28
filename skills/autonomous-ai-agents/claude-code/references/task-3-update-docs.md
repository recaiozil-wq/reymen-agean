---
skill_id: 4f7b436165f9
usage_count: 1
last_used: 2026-06-16
---
# Task 3: Update docs
terminal(command="tmux new-session -d -s task3 -x 140 -y 40 && tmux send-keys -t task3 'cd ~/project && claude -p \"Update README.md with the new API endpoints\" --allowedTools \"Read,Edit\" --max-turns 5' Enter")