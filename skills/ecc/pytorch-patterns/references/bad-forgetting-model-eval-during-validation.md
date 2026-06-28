---
skill_id: 31ff0629de6e
usage_count: 1
last_used: 2026-06-16
---
# Bad: Forgetting model.eval() during validation
model.train()
with torch.no_grad():
    output = model(val_data)  # Dropout still active! BatchNorm uses batch stats!