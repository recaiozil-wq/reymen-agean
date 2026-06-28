---
skill_id: 13103b2de4d6
usage_count: 1
last_used: 2026-06-16
---
## 3. Managing Issues

### Add/Remove Labels

**With gh:**

```bash
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --remove-label "needs-triage"
```

**With curl:**

```bash