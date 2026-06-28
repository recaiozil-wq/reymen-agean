---
skill_id: 68a46f0cd391
usage_count: 1
last_used: 2026-06-16
---
## Locator Strategy

```
AutomationId  >  Name (text)  >  ClassName + index  >  XPath
  (stable)         (readable)       (fragile)           (last resort)
```

Inspect with Accessibility Insights → **Properties** pane → look for `AutomationId` first.

```python