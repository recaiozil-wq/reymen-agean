---
skill_id: 51d30994f613
usage_count: 1
last_used: 2026-06-16
---
# Re-run BOTH reviewers on fixed output (fresh agents, no memory of previous round)
    review_b = Agent(prompt=REVIEWER_PROMPT.format(output=output, ...))
    review_c = Agent(prompt=REVIEWER_PROMPT.format(output=output, ...))