---
skill_id: c3309736186f
usage_count: 1
last_used: 2026-06-16
---
# Configure your language model
lm = dspy.Claude(model="claude-sonnet-4-5-20250929")
dspy.settings.configure(lm=lm)