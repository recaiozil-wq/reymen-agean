---
skill_id: 1bac2499d847
usage_count: 1
last_used: 2026-06-16
---
# Create artifact
artifact = wandb.Artifact(
    name='training-dataset',
    type='dataset',
    description='ImageNet training split',
    metadata={'size': '1.2M images', 'split': 'train'}
)