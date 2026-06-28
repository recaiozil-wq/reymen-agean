---
skill_id: 3056b4b07645
usage_count: 1
last_used: 2026-06-16
---
## Core Architecture

```
User Query
    │
    ▼
┌──────────────────────────┐
│  Rule-Based Decision     │  ← First: check explicit rules
│  (Clear intent → action) │
└──────────┬───────────────┘
           │ Ambiguous / low confidence
           ▼
┌──────────────────────────┐
│  MAB Engine              │  ← Fallback: Thompson Sampling
│  (Best historical match) │      or Epsilon-Greedy
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Action → Response       │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│  Reward Signal           │  ← User correction, task completion,
│  (Feedback loop)         │      silence, or explicit approval
└──────────┬───────────────┘
           │
           ▼
     Update model
```