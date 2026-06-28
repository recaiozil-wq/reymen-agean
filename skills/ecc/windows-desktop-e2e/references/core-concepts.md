---
skill_id: 15cbce4f4e0f
usage_count: 1
last_used: 2026-06-16
---
## Core Concepts

All Windows desktop automation relies on **UI Automation (UIA)**, a Windows-built-in accessibility API. Every supported framework exposes a tree of UIA elements with properties Claude can read and act on:

```
Your test (Python)
    └── pywinauto (UIA backend)
        └── Windows UI Automation API   ← built into Windows, framework-agnostic
            └── App's UIA provider      ← each framework ships its own
                └── Running .exe
```

**UIA quality by framework:**

| Framework | AutomationId | Reliability | Notes |
|-----------|-------------|-------------|-------|
| WPF | ★★★★★ | Excellent | `x:Name` maps directly to AutomationId |
| WinForms | ★★★★☆ | Good | `AccessibleName` = AutomationId |
| UWP / WinUI 3 | ★★★★★ | Excellent | Full Microsoft support |
| Qt 6.x | ★★★★★ | Excellent | Accessibility enabled by default; class names change to `Qt6*` |
| Qt 5.15+ | ★★★★☆ | Good | Improved Accessibility module |
| Qt 5.7–5.14 | ★★★☆☆ | Fair | Needs `QT_ACCESSIBILITY=1`; objectName manual |
| Win32 / MFC | ★★★☆☆ | Fair | Control IDs accessible; text matching common |