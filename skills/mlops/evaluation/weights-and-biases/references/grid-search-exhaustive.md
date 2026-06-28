---
skill_id: 8b20533d5bbc
usage_count: 1
last_used: 2026-06-16
---
# Grid search - exhaustive
sweep_config = {
    'method': 'grid',
    'parameters': {
        'lr': {'values': [0.001, 0.01, 0.1]},
        'batch_size': {'values': [16, 32, 64]}
    }
}