---
skill_id: 27a9e95859ec
usage_count: 1
last_used: 2026-06-16
---
# Good: Always set eval mode
model.eval()
with torch.no_grad():
    output = model(val_data)