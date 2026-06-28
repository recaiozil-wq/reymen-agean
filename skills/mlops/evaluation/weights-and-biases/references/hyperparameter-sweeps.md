---
skill_id: 6b75df63d261
usage_count: 1
last_used: 2026-06-16
---
## Hyperparameter Sweeps

Automatically search for optimal hyperparameters.

### Define Sweep Configuration

```python
sweep_config = {
    'method': 'bayes',  # or 'grid', 'random'
    'metric': {
        'name': 'val/accuracy',
        'goal': 'maximize'
    },
    'parameters': {
        'learning_rate': {
            'distribution': 'log_uniform',
            'min': 1e-5,
            'max': 1e-1
        },
        'batch_size': {
            'values': [16, 32, 64, 128]
        },
        'optimizer': {
            'values': ['adam', 'sgd', 'rmsprop']
        },
        'dropout': {
            'distribution': 'uniform',
            'min': 0.1,
            'max': 0.5
        }
    }
}