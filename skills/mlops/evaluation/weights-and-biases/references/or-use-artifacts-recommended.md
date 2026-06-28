---
skill_id: 693d602eb9ee
usage_count: 1
last_used: 2026-06-16
---
# Or use Artifacts (recommended)
artifact = wandb.Artifact('model', type='model')
artifact.add_file('checkpoint.pth')
wandb.log_artifact(artifact)
```