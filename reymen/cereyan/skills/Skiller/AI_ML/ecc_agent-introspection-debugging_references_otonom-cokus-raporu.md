---
name: ecc_agent-introspection-debugging_references_otonom-cokus-raporu
description: Otonom Çöküş Raporu (Crash Report / Human-in-the-Loop Handoff)
title: "Ecc Agent Introspection Debugging References Otonom Cokus Raporu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Otonom Çöküş Raporu (Crash Report / Human-in-the-Loop Handoff) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Otonom Çöküş Raporu (Crash Report / Human-in-the-Loop Handoff)

## Ne İşe Yarar
Ajanın otonom çözüm sınırları tükendiğinde, insan-okunabilir formatlı bir "otopsi raporu" üretir ve görevi kullanıcıya devreder.

## Kullanım Şekli
```python
from cokus_raporlayici import cokus_raporu_uret

# Maks tur aşılınca veya circuit breaker tetiklenince:
rapor = cokus_raporu_uret(
    gorev=hedef,
    deneme_sayisi=max_tur,
    hata_gecmisi=adim_gecmisi[-10:],
    denenen_ajanlar=["genel_cozucu", "kod_uzmani"],
    tiklanma_nedeni="Son gozlem: ..."
)
# Rapor .ReYMeN/cokus_raporlari/cokus_YYYYMMDD_HHMMSS.txt'ye kaydedilir
```

## Rapor Formatı
```
============================================================
🚨 [OTONOM SISTEM COKUS / TAHLIYE RAPORU] 🚨
============================================================
Kritik Zaman Dilimi    : 2026-06-17 08:38:15
Basarisiz Olunan Gorev : Web'den veri cekme
Toplam Tuketilen Dongu : 10 Tur

🔍 [KRONOLOJIK HATA VE ADAPTASYON GECMISI]
  [1] web_scraper -> HTTP 403 Forbidden
  [2] html_parse -> SyntaxError
  [3] api_gateway -> TimeoutError

🧠 [GOREV SURESINCE DENENEN AJANLAR]
genel_cozucu, kod_uzmani, sistem_mimari

⚠️ [OLUMCUL KILITLENME NOKTASI (KOK NEDEN)]
API rate limit + SSL sertifikasi uyusmazligi.

🚨 KULLANICI ACIL MUDAHALE PROTOKOLU
Lutfen cozum onerisini yeni bir gorev olarak iletin.
```

## Avantajları
- İnsanın anlayacağı formatta, hemen aksiyona geçebilir
- Zaman damgalı, `.ReYMeN/cokus_raporlari/` altında saklanır
- Kullanıcıya "ne oldu, hangi ajan denendi, son hata ne" net bilgi verir
- Çözüm önerisi Yetenek Fabrikası'na beslenebilir
