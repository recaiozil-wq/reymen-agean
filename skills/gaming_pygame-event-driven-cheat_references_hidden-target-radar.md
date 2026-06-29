
> **Kategori:** Gaming

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Gaming_Pygame Event Driven Cheat_References_Hidden Target Radar |
| **Nerede?** | Gaming/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Hidden Target Radar Pattern

- `hidden_targets` listesi: `[{'rect': Rect(x,y,10,10), 'found': False}, ...]`.
- Radar kapalı: hedef 2 px gri `draw.circle`.
- Radar açık: hedef 8 px yarı saydam kırmızı `draw.circle` + sağ altta mini daire harita.
- Radar çiziminde oyuncu merkez; hedefler/düşmanlar relative offset mini dairede.
