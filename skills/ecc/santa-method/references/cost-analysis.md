---
skill_id: 635b8c587209
usage_count: 1
last_used: 2026-06-16
---
## Cost Analysis

Santa Method costs approximately 2-3x the token cost of generation alone per verification cycle. For most high-stakes output, this is a bargain:

```
Cost of Santa = (generation tokens) + 2×(review tokens per round) × (avg rounds)
Cost of NOT Santa = (reputation damage) + (correction effort) + (trust erosion)
```

For batch operations, the sampling pattern reduces cost to ~15-20% of full verification while catching >90% of systematic issues.