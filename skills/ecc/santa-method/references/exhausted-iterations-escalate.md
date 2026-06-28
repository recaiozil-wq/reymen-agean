---
skill_id: 6c8fdd48e712
usage_count: 1
last_used: 2026-06-16
---
# Exhausted iterations — escalate
log_santa_result(output, MAX_ITERATIONS, "escalated")
escalate_to_human(output, issues)
```

Critical: each review round uses **fresh agents**. Reviewers must not carry memory from previous rounds, as prior context creates anchoring bias.