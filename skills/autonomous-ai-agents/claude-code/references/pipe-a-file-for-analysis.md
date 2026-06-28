---
skill_id: f8ff8e95a04b
usage_count: 1
last_used: 2026-06-16
---
# Pipe a file for analysis
terminal(command="cat src/auth.py | claude -p 'Review this code for bugs' --max-turns 1", timeout=60)