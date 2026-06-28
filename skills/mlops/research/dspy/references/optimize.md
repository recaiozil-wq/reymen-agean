---
skill_id: c14f7a753888
usage_count: 1
last_used: 2026-06-16
---
# Optimize
optimizer = BootstrapFewShot(metric=validate_answer, max_bootstrapped_demos=3)
optimized_qa = optimizer.compile(qa, trainset=trainset)