---
skill_id: 15903b712166
usage_count: 1
last_used: 2026-06-16
---
# Use cheap model for retrieval, strong model for reasoning
with dspy.settings.context(lm=cheap_lm):
    context = retriever(question)

with dspy.settings.context(lm=strong_lm):
    answer = generator(context=context, question=question)
```