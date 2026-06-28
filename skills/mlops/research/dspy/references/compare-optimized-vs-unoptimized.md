---
skill_id: 2e5c46d2f793
usage_count: 1
last_used: 2026-06-16
---
# Compare optimized vs unoptimized
score_before = evaluator(qa)
score_after = evaluator(optimized_qa)
print(f"Improvement: {score_after - score_before:.2%}")
```