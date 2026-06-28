---
skill_id: eeca508c2d19
usage_count: 1
last_used: 2026-06-16
---
# Step 2: De-sloppify (cleanup pass)
claude -p "Review all files changed by the previous commit. Remove any unnecessary type tests, overly defensive checks, or testing of language features (e.g., testing that TypeScript generics work). Keep real business logic tests. Run the test suite after cleanup."