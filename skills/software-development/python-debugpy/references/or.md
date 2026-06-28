---
skill_id: e81c4e4f2b7b
usage_count: 1
last_used: 2026-06-16
---
# or
source .venv/bin/activate
python -m pytest tests/foo_test.py::test_bar --pdb
```

This bypasses the hermetic-env guarantees — fine for debugging, but re-run under the wrapper to confirm before pushing.