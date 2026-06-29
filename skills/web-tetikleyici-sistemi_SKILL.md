---
name: web-tetikleyici-sistemi
title: Web Tetikleyici Sistemi
description: 5 tetikleyici ile ajanin ne zaman web'e gidecegini otomatik belirleme.
---


> **Kategori:** Kod

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | 5 tetikleyici ile ajanin ne zaman web'e gidecegini otomatik belirleme. |
| **Nerede?** | Kod/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Web Tetikleyici Sistemi

## 5 Tetikleyici (Öncelik Sırasıyla)

| # | Tetikleyici | Kosul | Puan | Ne Zaman? |
|:-:|:------------|:------|:----|:----------|
| 1 | **T1: Hafiza bos** | `COUNT=0` | 1.0 | Yeni tool/kategori hic bilinmiyor |
| 2 | **T3: Gorev basarisiz** | `hata >= 2` | 0.8 | 2. hatadan sonra web'de cozum ara |
| 3 | **T2: Guven dusuk** | `guven < 0.5` | 0.5-0.3 | 1 basari 3 hata = guven 0.25 |
| 4 | **T4: Gecerlilik asmis** | `tarih < bugun` | 0.3 | 6+ ay once ogrenilmis bilgi |
| 5 | **T5: Celiski** | `icerik1 != icerik2` | 0.6-0.4 | Video/Kullanici farkli soyluyor |

## Akış

```
GÖREV GELDİ
  ↓
T1: Hafizada kayit var mi?
  ├─ HAYIR → WEB'E GİT (direkt)
  └─ EVET → devam
              ↓
T3: hata_sayisi >= 2 mi?
  ├─ EVET → WEB'E GİT (cozum ara)
  └─ HAYIR → devam
              ↓
T2: guven_skoru < 0.5 mi?
  ├─ EVET → WEB'E GİT (dogrula)
  └─ HAYIR → devam
              ↓
T4: gecerlilik_tarihi < bugun mu?
  ├─ EVET → WEB'E GİT (arka planda tazele)
  └─ HAYIR → devam
              ↓
T5: Iki kaynak celisiyor mu?
  ├─ EVET → WEB'E GİT (hakem karar)
  └─ HAYIR → HAFIZADAN KULLAN
```

## Veritabanı

`ogrenmeler` tablosuna eklenen kolon:
- `web_arama_sebebi TEXT DEFAULT ''` — neden arama yapildi?

## Test

```python
from _web_tetikleyici import web_gerekli_mi

ateslendi, sebep, puan = web_gerekli_mi("yeni_tool", hata_sayisi=0)
if ateslendi:
    web_search(sebep)  # web'de ara
else:
    once_hafiza.ara(hedef)  # hafizadan kullan
```