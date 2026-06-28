---
skill_id: ed75de71336b
usage_count: 1
last_used: 2026-06-16
---
# Initialize a run
run = wandb.init(
    project="my-project",
    config={
        "learning_rate": 0.001,
        "epochs": 10,
        "batch_size": 32,
        "architecture": "ResNet50"
    }
)