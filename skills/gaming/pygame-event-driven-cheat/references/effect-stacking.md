---
skill_id: 797c912beeae
usage_count: 1
last_used: 2026-06-16
---
# Effect Stacking Rules

- Speed = base * (2 if speed_boost > 0 else 1) * (2 if sprint_timer > 0 else 1)
- Slow = game_speed = 0.5 when slow_timer > 0 else 1.0
- Magnet: 150 px içindeki hedefleri oyuncuya doğru çek.
- Freeze: düşmanlar `move_enemy_randomly` çağrısını atla.
- Global counter: `hile_sayisi`.
- Running effects printed: "AKTİF HİLELER: ...".
