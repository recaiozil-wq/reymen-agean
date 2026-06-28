---
skill_id: 4f68ac8e63a2
usage_count: 1
last_used: 2026-06-16
---
# Add callback
model.fit(
    x_train, y_train,
    validation_data=(x_val, y_val),
    epochs=10,
    callbacks=[WandbCallback()]  # Auto-logs metrics
)
```