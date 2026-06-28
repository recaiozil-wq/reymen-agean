---
skill_id: 759bcdda9eb5
usage_count: 1
last_used: 2026-06-16
---
# GOOD: assert on content / state
assert page.get_text(page.by_id("lblStatus")) == "Logged in"
assert page.by_id("btnLogout").is_enabled()
```

```python