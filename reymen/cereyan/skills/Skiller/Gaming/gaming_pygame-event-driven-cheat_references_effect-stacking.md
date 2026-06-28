
> **Kategori:** Gaming

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Gaming_Pygame Event Driven Cheat_References_Effect Stacking |
| **Nerede?** | Gaming/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Effect Stacking Rules

- Speed = base * (2 if speed_boost > 0 else 1) * (2 if sprint_timer > 0 else 1)
- Slow = game_speed = 0.5 when slow_timer > 0 else 1.0
- Magnet: 150 px içindeki hedefleri oyuncuya doğru çek.
- Freeze: düşmanlar `move_enemy_randomly` çağrısını atla.
- Global counter: `hile_sayisi`.
- Running effects printed: "AKTİF HİLELER: ...".
