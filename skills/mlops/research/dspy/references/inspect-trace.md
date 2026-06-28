---
skill_id: 512293a12422
usage_count: 1
last_used: 2026-06-16
---
# Inspect trace
for call in dspy.settings.trace:
    print(f"Prompt: {call['prompt']}")
    print(f"Response: {call['response']}")
```