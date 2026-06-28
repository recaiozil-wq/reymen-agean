---
skill_id: ba7d10eac806
usage_count: 1
last_used: 2026-06-16
---
# Define a signature (input → output)
class QA(dspy.Signature):
    """Answer questions with short factual answers."""
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 1 and 5 words")