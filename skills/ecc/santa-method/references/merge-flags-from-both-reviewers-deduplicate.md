---
skill_id: 78d6636e6bad
usage_count: 1
last_used: 2026-06-16
---
# Merge flags from both reviewers, deduplicate
    all_issues = dedupe(review_b.critical_issues + review_c.critical_issues)
    all_suggestions = dedupe(review_b.suggestions + review_c.suggestions)

    return "NAUGHTY", all_issues, all_suggestions
```

Why both must pass: if only one reviewer catches an issue, that issue is real. The other reviewer's blind spot is exactly the failure mode Santa Method exists to eliminate.

### Phase 4: Fix Until Nice (Convergence Loop)

```python
MAX_ITERATIONS = 3

for iteration in range(MAX_ITERATIONS):
    verdict, issues, suggestions = santa_verdict(review_b, review_c)

    if verdict == "NICE":
        log_santa_result(output, iteration, "passed")
        return ship(output)