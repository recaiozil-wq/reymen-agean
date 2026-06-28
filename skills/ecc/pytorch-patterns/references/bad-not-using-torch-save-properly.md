---
skill_id: 62f011005baf
usage_count: 1
last_used: 2026-06-16
---
# Bad: Not using torch.save properly
torch.save(model, "model.pt")  # Saves entire model (fragile, not portable)