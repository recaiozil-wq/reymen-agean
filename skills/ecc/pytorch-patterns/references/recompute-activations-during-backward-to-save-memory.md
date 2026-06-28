---
skill_id: e91bf2a8a4b0
usage_count: 1
last_used: 2026-06-16
---
# Recompute activations during backward to save memory
        x = checkpoint(self.block1, x, use_reentrant=False)
        x = checkpoint(self.block2, x, use_reentrant=False)
        return self.head(x)
```

### torch.compile for Speed

```python