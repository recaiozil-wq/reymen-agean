---
skill_id: 68403797f678
usage_count: 1
last_used: 2026-06-16
---
## Debugging Failures

1. Re-run the single failing test with gtest filter.
2. Add scoped logging around the failing assertion.
3. Re-run with sanitizers enabled.
4. Expand to full suite once the root cause is fixed.