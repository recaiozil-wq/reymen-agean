---
skill_id: ffff488927e2
usage_count: 1
last_used: 2026-06-16
---
# Expect 19 passed, 0 xfailed against the s6 image
```

The harness lives in `tests/docker/` and skips when Docker isn't available. The per-test timeout is bumped to 180s (see `tests/docker/conftest.py`).