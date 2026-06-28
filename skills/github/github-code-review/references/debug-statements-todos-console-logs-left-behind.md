---
skill_id: a0e7f5b621b4
usage_count: 1
last_used: 2026-06-16
---
# Debug statements, TODOs, console.logs left behind
git diff main...HEAD | grep -n "print(\|console\.log\|TODO\|FIXME\|HACK\|XXX\|debugger"