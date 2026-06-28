---
skill_id: 13983d783da7
usage_count: 1
last_used: 2026-06-16
---
# Good: Move model once before the loop
model = model.to(device)
for data, target in dataloader:
    data, target = data.to(device), target.to(device)