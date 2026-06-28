---
skill_id: cecaa97b05bc
usage_count: 1
last_used: 2026-06-16
---
# Create W&B logger
wandb_logger = WandbLogger(
    project="lightning-demo",
    log_model=True  # Log model checkpoints
)