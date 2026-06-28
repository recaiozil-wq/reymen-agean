---
skill_id: a4668b94a91e
usage_count: 1
last_used: 2026-06-16
---
# Detect flaky tests (repeat each 5 times)
pip install pytest-repeat
pytest tests/test_login.py --count=5 -v
```