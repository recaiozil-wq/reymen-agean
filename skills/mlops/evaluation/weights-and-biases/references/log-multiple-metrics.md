---
skill_id: 8a666f330942
usage_count: 1
last_used: 2026-06-16
---
# Log multiple metrics
wandb.log({
    "train/loss": train_loss,
    "train/accuracy": train_acc,
    "val/loss": val_loss,
    "val/accuracy": val_acc,
    "learning_rate": current_lr,
    "epoch": epoch
})