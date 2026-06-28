---
skill_id: ceb41978ce4b
usage_count: 1
last_used: 2026-06-16
---
# Bad: Only saving model weights (can't resume training)
torch.save(model.state_dict(), "model.pt")
```