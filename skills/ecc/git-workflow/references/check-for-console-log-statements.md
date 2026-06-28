---
skill_id: e56ccf58ea9d
usage_count: 1
last_used: 2026-06-16
---
# Check for console.log statements
if git diff origin/main | grep -E 'console\.log'; then
    echo "Remove console.log statements before pushing."
    exit 1
fi
```