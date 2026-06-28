---
skill_id: d6ccf2800a92
usage_count: 1
last_used: 2026-06-16
---
# Training loop
    for epoch in range(NUM_EPOCHS):
        train_loss = train_epoch(model, optimizer, batch_size)
        val_acc = validate(model)