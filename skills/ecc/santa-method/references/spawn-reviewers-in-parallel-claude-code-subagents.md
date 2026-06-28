---
skill_id: fc4cd39c6852
usage_count: 1
last_used: 2026-06-16
---
# Spawn reviewers in parallel (Claude Code subagents)
review_b = Agent(prompt=REVIEWER_PROMPT.format(...), description="Santa Reviewer B")
review_c = Agent(prompt=REVIEWER_PROMPT.format(...), description="Santa Reviewer C")