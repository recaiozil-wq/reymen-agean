---
skill_id: 72e587e4247a
usage_count: 1
last_used: 2026-06-16
---
# Use validation set for metric
def metric(example, pred, trace=None):
    return example.answer in pred.answer
```

### 4. Save and Load Optimized Models

```python