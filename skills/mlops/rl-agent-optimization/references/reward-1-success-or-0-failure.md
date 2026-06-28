---
skill_id: 91c66456bb1e
usage_count: 1
last_used: 2026-06-16
---
# reward = 1 (success) or 0 (failure)
        if reward == 1:
            self.alpha[arm] = self.alpha.get(arm, 1) + 1
        else:
            self.beta[arm] = self.beta.get(arm, 1) + 1
```

**Alternative: Epsilon-Greedy** (simpler, less data-efficient):
- 90% of the time: pick the arm with highest historical success rate
- 10% of the time: pick a random arm (exploration)

### Phase 3 — Shadow Mode Deployment

Never switch from rules to MAB cold-turkey. Run in shadow mode:

1. **Rules make the real decision** — system behaves normally
2. **MAB makes a parallel decision** — logged for comparison
3. **Track divergence rate** — when MAB disagrees with rules, who was right?
4. **Switch threshold** — only switch when MAB matches or exceeds rule accuracy for 100+ consecutive decisions
5. **Emergency rollback** — keep the last-known-good rule snapshot

### Phase 4 — Hybrid Decision Layer

The final system doesn't replace rules — it supplements them:

```python