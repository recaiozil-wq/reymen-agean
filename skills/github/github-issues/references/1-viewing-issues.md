---
skill_id: 050ebe1354ad
usage_count: 1
last_used: 2026-06-16
---
## 1. Viewing Issues

**With gh:**

```bash
gh issue list
gh issue list --state open --label "bug"
gh issue list --assignee @me
gh issue list --search "authentication error" --state all
gh issue view 42
```

**With curl:**

```bash