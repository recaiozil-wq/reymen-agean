---
skill_id: 0d088fa7b17b
usage_count: 1
last_used: 2026-06-16
---
# Bad: In-place operations breaking autograd
x = F.relu(x, inplace=True)  # Can break gradient computation
x += residual                  # In-place add breaks autograd graph