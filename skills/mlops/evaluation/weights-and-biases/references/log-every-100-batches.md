---
skill_id: 19b9e2948719
usage_count: 1
last_used: 2026-06-16
---
# Log every 100 batches
        if batch_idx % 100 == 0:
            wandb.log({
                "loss": loss.item(),
                "epoch": epoch,
                "batch": batch_idx
            })