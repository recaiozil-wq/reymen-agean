---
skill_id: c23e6ad46584
usage_count: 1
last_used: 2026-06-16
---
## Critical Workflow Order

Discovered empirically 14 June 2026 after a 622-skill seed produced 4.3% accuracy.

```
CORRECT ORDER:    reward_validation → fix_reward → seed_gradually → test_shadow → deploy
WRONG ORDER:      seed_all → test → find_empty_reward → backtrack
```

The wrong order wastes days. Validate the reward function first because:
- A bad reward function corrupts every MAB update (beta values inflate from false negatives)
- You cannot tell if MAB is bad or the reward signal is bad without separate validation
- Seeding 622 skills with neutral priors sounds productive but just turns MAB into a random selector (all arms equal)