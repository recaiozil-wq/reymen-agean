---
skill_id: 817a850648d9
usage_count: 1
last_used: 2026-06-16
---
# Save model
torch.save(model.state_dict(), "model.pth")
wandb.save("model.pth")  # Upload to W&B

wandb.finish()
```