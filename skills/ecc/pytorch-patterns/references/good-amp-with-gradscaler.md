---
skill_id: d383b13eec87
usage_count: 1
last_used: 2026-06-16
---
# Good: AMP with GradScaler
scaler = torch.amp.GradScaler("cuda")
for data, target in dataloader:
    with torch.amp.autocast("cuda"):
        output = model(data)
        loss = criterion(output, target)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
    optimizer.zero_grad(set_to_none=True)
```

### Gradient Checkpointing for Large Models

```python