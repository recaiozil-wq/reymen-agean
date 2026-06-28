---
skill_id: 6fb7befdb9cb
usage_count: 1
last_used: 2026-06-16
---
# Use it
response = qa(question="What is the capital of France?")
print(response.answer)  # "Paris"
```

### Chain of Thought Reasoning

```python
import dspy

lm = dspy.Claude(model="claude-sonnet-4-5-20250929")
dspy.settings.configure(lm=lm)