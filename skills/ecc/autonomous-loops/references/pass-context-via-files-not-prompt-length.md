---
skill_id: 72eeebbea180
usage_count: 1
last_used: 2026-06-16
---
# Pass context via files, not prompt length
echo "Focus areas: auth module, API rate limiting" > .claude-context.md
claude -p "Read .claude-context.md for priorities. Work through them in order."
rm .claude-context.md
```

**With `--allowedTools` restrictions:**
```bash