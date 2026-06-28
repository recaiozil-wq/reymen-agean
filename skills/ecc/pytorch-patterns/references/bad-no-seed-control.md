---
skill_id: 06de0aa673dc
usage_count: 1
last_used: 2026-06-16
---
# Bad: No seed control
model = MyModel()  # Different weights every run
```

### 3. Explicit Shape Management

Always document and verify tensor shapes.

```python