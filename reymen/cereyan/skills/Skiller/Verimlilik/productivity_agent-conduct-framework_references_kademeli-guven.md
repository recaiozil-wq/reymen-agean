
> **Kategori:** Verimlilik

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Productivity_Agent Conduct Framework_References_Kademeli Guven |
| **Nerede?** | Verimlilik/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Kademeli Güven Skoru (Sigmoid)

## Formül

```python
guven = 1.0 / (1.0 + math.exp(-0.5 * (basari - hata - 1)))
```

## Değerler

| Basari | Hata | Net | Guven | Anlamı |
|:------|:-----|:----|:------|:-------|
| 1 | 0 | 0 | **0.50** | İlk başarı — başlangıç |
| 2 | 0 | 1 | 0.62 | |
| 3 | 0 | 2 | 0.73 | |
| 5 | 0 | 4 | 0.88 | > 0.8 → LLM atlanır |
| 10 | 0 | 9 | 0.99 | Neredeyse kesin |
| 1 | 1 | -1 | 0.27 | 1 başarı 1 hata |
| 1 | 3 | -3 | 0.08 | Çok güvensiz |

## Neden Lineer Değil?

Eski formül: `guven = basari / (basari + hata)`
- İlk başarıda 1/1 = 1.0 (çok yüksek)
- 1 başarı 1 hatada 0.5 (çok düşük)

Yeni formül (sigmoid):
- İlk başarıda 0.5 (orta)
- 3 başarıda 0.73 (yeterli)
- 10 başarıda 0.99 (kesin)
- Hata oranı arttıkça daha hızlı düşer

## LLM Atlama Eşiği

`guven > 0.8` → LLM çağrılmaz, direkt hafızadan döndürülür.
Bu eşiğe ulaşmak için: 5 başarı 0 hata (veya 4 başarı 0 hata ≈ 0.82)
