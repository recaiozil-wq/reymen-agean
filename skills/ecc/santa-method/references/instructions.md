---
skill_id: cbde2df6a7c8
usage_count: 1
last_used: 2026-06-16
---
## Instructions
Evaluate the output against EACH rubric criterion. For each:
- PASS: criterion fully met, no issues
- FAIL: specific issue found (cite the exact problem)

Return your assessment as structured JSON:
{
  "verdict": "PASS" | "FAIL",
  "checks": [
    {"criterion": "...", "result": "PASS|FAIL", "detail": "..."}
  ],
  "critical_issues": ["..."],   // blockers that must be fixed
  "suggestions": ["..."]         // non-blocking improvements
}

Be rigorous. Your job is to find problems, not to approve.
"""
```

```python