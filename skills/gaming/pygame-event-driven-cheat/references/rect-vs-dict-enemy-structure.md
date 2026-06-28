---
session: 2026-06-05
tags:
  - pygame
  - entity-structure
  - event-driven-refactor
---

## Event-Driven Refactor: Enemy Entity Structure

When the game state or enemy behavior needs to be extended after initial implementation, switching from `pygame.Rect`-based enemy records to dictionary structures avoids `AttributeError: 'pygame.rect.Rect' object has no attribute 'dir'`.

### Root Cause
Enemies defined as plain `pygame.Rect(x, y, w, h)` have no `dir` attribute. Once movement/direction logic is added after creation, the code tries to read `enemy['dir']` and crashes.

### Survivability Checklist
- Use dict from the start if behavior may grow:
  - `{"rect": pygame.Rect(x, y, w, h), "dir": (dx, dy)}`
- Movement and collision checks must consistently read/write:
  - `enemy["rect"]`
  - `enemy["dir"]`
- Do not freeze entity type at import time; fields should be referenceable.

### Output Note
Observed/verified: game launched exit_code=0 after refactor.

---
Source: direct debug/trace on `eymen_oyun_hileleri.py` during in-session refactor of lines 48-98.
