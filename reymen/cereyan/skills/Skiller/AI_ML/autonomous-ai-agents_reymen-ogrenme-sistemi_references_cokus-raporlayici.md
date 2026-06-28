---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_cokus-raporlayici
description: Çöküş Raporlayıcı (cokus_raporlayici.py)
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Cokus Raporlayici"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Çöküş Raporlayıcı (cokus_raporlayici.py) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Çöküş Raporlayıcı (cokus_raporlayici.py)

Reymen'de otonom çözüm sınırları tükendiğinde insan-okunabilir crash raporu üreten sistem.

## Dosya

`cokus_raporlayici.py` — `cokus_raporu_uret()` fonksiyonu

## main.py Entegrasyonu (Maks Tur Aşımı)

```python
# main.py satır ~802
print("\n[MAKSIMUM TUR ASILDI]")
try:
    from cokus_raporlayici import cokus_raporu_uret
    _hata_gecmisi = [f"{a}" for a in adim_gecmisi[-10:]]
    cokus_raporu_uret(
        gorev=hedef,
        deneme_sayisi=max_tur,
        hata_gecmisi=_hata_gecmisi,
        denenen_ajanlar=["genel_cozucu"],
        tiklanma_nedeni=f"Son gozlem: {son_gozlem[:200] if son_gozlem else 'Bilinmiyor'}"
    )
except Exception as _cr_hata:
    print(f"[CokusRaporu] Hata: {_cr_hata}")
```

## Rapor Çıktısı

Klasör: `.ReYMeN/cokus_raporlari/cokus_YYYYMMDD_HHMMSS.txt`

Format:
```
============================================================
🚨 [OTONOM SISTEM COKUS / TAHLIYE RAPORU] 🚨
============================================================
Kritik Zaman Dilimi    : 2026-06-17 12:34:56
Basarisiz Olunan Gorev : Web'den veri cek
Toplam Tuketilen Dongu : 15 Tur

🔍 [KRONOLOJIK HATA VE ADAPTASYON GECMISI]
  [1] genel_cozucu: web_scraper -> HTTP 403
  [2] kod_uzmani: html_parse -> SyntaxError

🧠 [GOREV SURESINCE DENENEN AJANLAR]
genel_cozucu, kod_uzmani

⚠️ [OLUMCUL KILITLENME NOKTASI (KOK NEDEN)]
Son gozlem: HTTP 403 Forbidden

🚨 KULLANICI ACIL MUDAHALE VE GOREV DEVRİ PROTOKOLU
1. Yukaridaki verileri inceleyin
2. Bir COZUM ONERISI hazirlayin
3. Sisteme yeni gorev olarak iletin
```

## API

```python
from cokus_raporlayici import cokus_raporu_uret

rapor = cokus_raporu_uret(
    gorev="Gorev adi",
    deneme_sayisi=15,
    hata_gecmisi=["hata 1", "hata 2"],
    denenen_ajanlar=["genel_cozucu", "kod_uzmani"],
    tiklanma_nedeni="Son gozlem: ..."  # optional
)
# → Dosyaya yazılır ve string olarak döner
```

## Önemli

- Graceful degrade: import hatası alınırsa sessizce geçer (try/except ile)
- Klasör otomatik oluşturulur (`.ReYMeN/cokus_raporlari/`)
- Son 10 adım kaydedilir (adim_gecmisi[-10:])
- Rapor hem dosyaya yazılır hem string olarak döner
