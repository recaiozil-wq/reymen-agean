---
session: 2026-06-05
tags:
  - windows
  - screen-capture
  - multi-monitor
---

## Ursina Screen Capture Diagnostic

- `capture_screen_temp.ps1` failed on multi-monitor setup.
- Fix: use `[System.Windows.Forms.Screen]::PrimaryScreen.Bounds` as target rect.
  - UsePrimaryScreen bounds instead of AllScreens combos.
  - This eliminates `System.ArgumentException` from `CopyFromScreen` on multi-display expand.
- Verification: `C:\Users\marko\Desktop\screenshot.png` should be non-empty; screenshot visual inspection done.

---
Source: reproduction and fix session yielding `screenshot.png` (1536x960, 1.79MB) after applying patch.
