---
name: ecc_windows-desktop-e2e_references_core-concepts
description: Core Concepts
title: "Ecc Windows Desktop E2E References Core Concepts"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Core Concepts |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
