---
skill_id: 6a6a01c4e89e
usage_count: 1
last_used: 2026-06-16
---
# Different models for different tasks
cheap_lm = dspy.OpenAI(model="gpt-3.5-turbo")
strong_lm = dspy.Claude(model="claude-sonnet-4-5-20250929")