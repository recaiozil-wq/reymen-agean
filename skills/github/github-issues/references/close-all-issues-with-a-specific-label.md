---
skill_id: 81cbd11c5fc8
usage_count: 1
last_used: 2026-06-16
---
# Close all issues with a specific label
gh issue list --label "wontfix" --json number --jq '.[].number' | \
  xargs -I {} gh issue close {} --reason "not planned"
```

**With curl:**

```bash