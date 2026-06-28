---
skill_id: 866aee1fddbc
usage_count: 1
last_used: 2026-06-16
---
## Integration with Other Skills

| Skill | Relationship |
|-------|-------------|
| Verification Loop | Use for deterministic checks (build, lint, test). Santa for semantic checks (accuracy, hallucinations). Run verification-loop first, Santa second. |
| Eval Harness | Santa Method results feed eval metrics. Track pass@k across Santa runs to measure generator quality over time. |
| Continuous Learning v2 | Santa findings become instincts. Repeated failures on the same criterion → learned behavior to avoid the pattern. |
| Strategic Compact | Run Santa BEFORE compacting. Don't lose review context mid-verification. |