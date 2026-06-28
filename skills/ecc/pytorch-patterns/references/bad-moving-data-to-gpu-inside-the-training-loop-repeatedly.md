---
skill_id: 984e8d4f2bd2
usage_count: 1
last_used: 2026-06-16
---
# Bad: Moving data to GPU inside the training loop repeatedly
for data, target in dataloader:
    model = model.cuda()  # Moves model EVERY iteration!