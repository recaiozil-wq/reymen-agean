---
skill_id: 485b1505a71e
usage_count: 1
last_used: 2026-06-16
---
## Why Hooks vs Skills for Observation?

> "v1 relied on skills to observe. Skills are probabilistic -- they fire ~50-80% of the time based on Claude's judgment."

Hooks fire **100% of the time**, deterministically. This means:
- Every tool call is observed
- No patterns are missed
- Learning is comprehensive