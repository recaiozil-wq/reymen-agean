---
skill_id: e0f54a6e3f33
usage_count: 1
last_used: 2026-06-16
---
# Event-Driven Input Pattern

`pygame.event.get()` döngüde `KEYDOWN` üzerinden tuşları yakala.
`get_pressed()` yerine event key kullanarak tetikle.

```python
if event.type == pygame.KEYDOWN:
    if event.key == pygame.K_ESCAPE:
        running = False
    elif event.key in cheat_map:
        msg = apply_cheat(event.key)
```

Cooldown params:
```python
CHEAT_COOLDOWN_MS = 120
if now - last_cheat_time > CHEAT_COOLDOWN_MS:
    last_cheat_time = now
    apply_cheat(...)
```
