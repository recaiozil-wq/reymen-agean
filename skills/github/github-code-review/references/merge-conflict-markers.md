---
skill_id: bbb68c6a1142
usage_count: 1
last_used: 2026-06-16
---
# Merge conflict markers
git diff main...HEAD | grep -n "<<<<<<\|>>>>>>\|======="
```

4. **Present structured feedback** to the user.

### Review Output Format

When reviewing local changes, present findings in this structure:

```