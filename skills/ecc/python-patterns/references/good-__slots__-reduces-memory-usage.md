---
skill_id: 0175c26cace0
usage_count: 1
last_used: 2026-06-16
---
# Good: __slots__ reduces memory usage
class Point:
    __slots__ = ['x', 'y']

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
```

### Generator for Large Data

```python