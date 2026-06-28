---
skill_id: 249573759630
usage_count: 1
last_used: 2026-06-16
---
## Backward Compatibility

v2.1 is fully compatible with v2.0 and v1:
- Existing global instincts can be migrated from `~/.claude/homunculus/instincts/` with `scripts/migrate-homunculus.sh`
- Existing `~/.claude/skills/learned/` skills from v1 still work
- Stop hook still runs (but now also feeds into v2)
- Gradual migration: run both in parallel