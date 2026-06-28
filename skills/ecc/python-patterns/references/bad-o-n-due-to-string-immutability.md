---
skill_id: b34b1117caf1
usage_count: 1
last_used: 2026-06-16
---
# Bad: O(n²) due to string immutability
result = ""
for item in items:
    result += str(item)