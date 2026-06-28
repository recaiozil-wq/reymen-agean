---
skill_id: abd4054dbd48
usage_count: 1
last_used: 2026-06-16
---
#    Same SHA = no tampering. Different = review changes.
```

### Usefulness Scoring (10-point scale)

| Criterion | Weight | What to check |
|-----------|--------|--------------|
| ReYMeN compatibility | 2 pts | Does it support ReYMeN? Skill.md format? |
| Coverage gap | 2 pts | Does it fill a gap in existing skills? |
| Code quality | 2 pts | Clean structure, tests, documentation |
| Security | 2 pts | No dangerous patterns, verified deps |
| Freshness | 1 pt | Recent commits, active maintenance |
| Language/docs | 1 pt | Are docs accessible? (Turkish/English vs Chinese) |

Score ≥7: Install. 4-6: Evaluate per-module. <4: Skip.

### Installation Methods

**Method A — npx skills add (simple skills):**
```bash