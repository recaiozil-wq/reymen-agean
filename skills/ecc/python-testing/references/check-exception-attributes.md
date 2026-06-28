---
skill_id: 7567d1d0f110
usage_count: 1
last_used: 2026-06-16
---
# Check exception attributes
with pytest.raises(ValueError) as exc_info:
    raise ValueError("error message")
assert str(exc_info.value) == "error message"
```