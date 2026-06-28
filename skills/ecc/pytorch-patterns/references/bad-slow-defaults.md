---
skill_id: 0343c0994884
usage_count: 1
last_used: 2026-06-16
---
# Bad: Slow defaults
dataloader = DataLoader(dataset, batch_size=32)  # num_workers=0, no pin_memory
```

### Custom Collate for Variable-Length Data

```python