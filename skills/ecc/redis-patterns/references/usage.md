---
skill_id: 9366282e11c1
usage_count: 1
last_used: 2026-06-16
---
# Usage
token = acquire_lock("order:payment:123")
if token:
    try:
        process_payment()
    finally:
        release_lock("order:payment:123", token)
```

> For multi-node setups use the `redlock-py` library which implements the full Redlock algorithm.