---
skill_id: 4c2852c033f5
usage_count: 1
last_used: 2026-06-16
---
# Bad: Hidden side effects
import some_module
some_module.setup()  # What does this do?
```

### 3. EAFP - Easier to Ask Forgiveness Than Permission

Python prefers exception handling over checking conditions.

```python