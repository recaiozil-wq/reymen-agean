
> **Kategori:** Gaming

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Gaming_Pygame Event Driven Cheat_References_Event Driven Input |
| **Nerede?** | Gaming/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

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
