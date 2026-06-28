---
skill_id: e13145d92ec7
usage_count: 1
last_used: 2026-06-16
---
# Create/use project
run = wandb.init(
    project="image-classification",
    name="resnet50-experiment-1",  # Optional run name
    tags=["baseline", "resnet"],    # Organize with tags
    notes="First baseline run"      # Add notes
)