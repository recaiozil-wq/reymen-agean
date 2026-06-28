---
skill_id: a799d7475047
usage_count: 1
last_used: 2026-06-16
---
# Use ChainOfThought for better reasoning
class MathProblem(dspy.Signature):
    """Solve math word problems."""
    problem = dspy.InputField()
    answer = dspy.OutputField(desc="numerical answer")