---
skill_id: e6f715eeeafd
usage_count: 1
last_used: 2026-06-16
---
# Mixed precision training
        with torch.amp.autocast("cuda", enabled=scaler is not None):
            output = model(data)
            loss = criterion(output, target)

        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            scaler.step(optimizer)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        total_loss += loss.item()

    return total_loss / len(dataloader)
```

### Validation Loop

```python