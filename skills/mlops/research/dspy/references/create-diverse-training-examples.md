---
skill_id: a67b0d055878
usage_count: 1
last_used: 2026-06-16
---
# Create diverse training examples
trainset = [
    dspy.Example(question="factual", answer="...).with_inputs("question"),
    dspy.Example(question="reasoning", answer="...").with_inputs("question"),
    dspy.Example(question="calculation", answer="...").with_inputs("question"),
]