---
skill_id: 84ebc0713a59
usage_count: 1
last_used: 2026-06-16
---
# Bad: Using .item() before backward
loss = criterion(output, target).item()  # Detaches from graph!
loss.backward()  # Error: can't backprop through .item()