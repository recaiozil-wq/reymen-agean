---
skill_id: 35a30d27959f
usage_count: 1
last_used: 2026-06-16
---
## Best Practices

### 1. Organize with Tags and Groups

```python
wandb.init(
    project="my-project",
    tags=["baseline", "resnet50", "imagenet"],
    group="resnet-experiments",  # Group related runs
    job_type="train"             # Type of job
)
```

### 2. Log Everything Relevant

```python