---
skill_id: a03e43f7b2fc
usage_count: 1
last_used: 2026-06-16
---
# Install ffmpeg and add to PATH: https://ffmpeg.org/download.html
```

Verify UIA is reachable:

```python
from pywinauto import Desktop
Desktop(backend="uia").windows()  # lists all top-level windows
```

Install **Accessibility Insights for Windows** (free, from Microsoft) — your DevTools equivalent for inspecting the UIA element tree before writing any test.