---
skill_id: a08286071c06
usage_count: 1
last_used: 2026-06-16
---
## Per-Step Trace (opt-in)

The default failure screenshot is often too thin for diagnosing flaky tests. The step-level trace below is **off by default** — enable it only when reproducing a flaky case.

### Enable

```bash
E2E_TRACE=1 pytest tests/test_login.py -v