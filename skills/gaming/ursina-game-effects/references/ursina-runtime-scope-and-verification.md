---
updated: 2026-06-05
tags:
  - ursina
  - runtime
  - debug
  - verification
---

## Ursina Runtime Scope, Verify, and Debug Loop

### Required Runtime Scope Global Declaration
- In `update()`, if `player_health` or `player_max_health` is assigned inside the function, add:
  `global player_health, player_max_health`
- Without this, readonly reads before assignment are fine, but any assignment later creates an `UnboundLocalError`.

### Compile → Launch → Capture → Analyze Cycle
1. `python -m py_compile C:\Users\marko\Desktop\minecraft_ursina.py`
2. Launch as background process.
3. Capture: powershell -NoProfile -ExecutionPolicy Bypass -File
   `C:\Users\marko\AppData\Local\hermes\scripts\capture_screen_temp.ps1`
4. Analyze screenshot for:
   - First-person camera/crosshair
   - 3D geometry and lighting
   - HUD/health text is readable

### Success Criteria for Verification
- No black/failed render
- Health text appears as expected
- If compile succeeds but screenshot shows blank, re-launch and re-capture instead of declaring success.

### Input Debounce Standard
- All manual cheat toggles require 350 ms debounce:
  `if now - last_toggle[key] < 0.35: return`

### Conditional Trigger Notes
- Verify `conditional_rules` use same scale as actual `player_max_health`.
- Example thresholds:
  - regen below 70%
  - resistance below 40%
