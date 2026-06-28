---
skill_id: 614125966bc0
usage_count: 1
last_used: 2026-06-16
---
# Create evaluator
evaluator = Evaluate(
    devset=testset,
    metric=exact_match,
    num_threads=4,
    display_progress=True
)