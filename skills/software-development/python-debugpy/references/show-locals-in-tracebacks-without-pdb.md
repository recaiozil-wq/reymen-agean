---
skill_id: 55d1b3dc748e
usage_count: 1
last_used: 2026-06-16
---
# Show locals in tracebacks without pdb:
scripts/run_tests.sh tests/path/to/test_file.py --showlocals --tb=long
```

Note: `scripts/run_tests.sh` uses xdist (`-n 4`) by default, and pdb does NOT work under xdist. Add `-p no:xdist` or run a single test with `-n 0`:

```bash
scripts/run_tests.sh tests/foo_test.py::test_bar --pdb -p no:xdist