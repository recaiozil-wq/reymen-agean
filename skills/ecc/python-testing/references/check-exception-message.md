---
skill_id: 3fef083b4563
usage_count: 1
last_used: 2026-06-16
---
# Check exception message
with pytest.raises(ValueError, match="invalid input"):
    raise ValueError("invalid input provided")