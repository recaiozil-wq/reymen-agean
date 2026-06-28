---
skill_id: dfbc13dffe75
usage_count: 1
last_used: 2026-06-16
---
# Bad: Hardcoded device
model = MyModel().cuda()  # Crashes if no GPU
data = data.cuda()
```

### 2. Reproducibility First

Set all random seeds for reproducible results.

```python