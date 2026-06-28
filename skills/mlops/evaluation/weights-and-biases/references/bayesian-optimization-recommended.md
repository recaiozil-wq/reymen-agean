---
skill_id: 0f90b654af2b
usage_count: 1
last_used: 2026-06-16
---
# Bayesian optimization (recommended)
sweep_config = {
    'method': 'bayes',
    'metric': {'name': 'val/loss', 'goal': 'minimize'},
    'parameters': {
        'lr': {'distribution': 'log_uniform', 'min': 1e-5, 'max': 1e-1}
    }
}
```