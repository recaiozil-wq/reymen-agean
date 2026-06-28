---
skill_id: ec4045dfb0c6
usage_count: 1
last_used: 2026-06-16
---
## Risk Mitigation

### Reward Hacking
The system will optimize whatever you reward. If you only reward speed, it gives shallow answers. If you only reward silence, it says nothing.

**Solution:** Multi-component reward:
```
reward = α * task_complete + β * (1 / corrections) + γ * quality_score - δ * cost
```

### Cold Start
With no data, MAB explores randomly. In the first 50-100 decisions, performance is worse than rules.

**Solution:** Seed the MAB with prior data from rule-based decisions. Use the first 50-100 rule decisions as initial training data before enabling MAB mode.

### Stability / Non-Stationarity
Users change. What worked last month may not work today. MAB adapts slowly.

**Solution:** Implement a sliding window (last 500 decisions) or exponential decay (older data weighted less).