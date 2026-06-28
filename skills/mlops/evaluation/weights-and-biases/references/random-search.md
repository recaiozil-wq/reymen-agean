---
skill_id: f4fe070ba829
usage_count: 1
last_used: 2026-06-16
---
# Random search
sweep_config = {
    'method': 'random',
    'parameters': {
        'lr': {'distribution': 'uniform', 'min': 0.0001, 'max': 0.1},
        'dropout': {'distribution': 'uniform', 'min': 0.1, 'max': 0.5}
    }
}