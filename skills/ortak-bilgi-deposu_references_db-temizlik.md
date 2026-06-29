---
name: ortak-bilgi-deposu_references_db-temizlik
description: DB Temizlik Cron
title: "Ortak Bilgi Deposu References Db Temizlik"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | DB Temizlik Cron |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# DB Temizlik Cron

Konum: `reymen/cereyan/temizlik_cron.sh`
Cron: Her gün 04:00'te çalışır (no_agent).

## Ne temizler?
1. **Geçerlilik tarihi geçmiş kayıtlar** (`gecerlilik_tarihi < bugun`)
2. **Düşük güvenli kayıtlar** (`guven_skoru < 0.2 VE hata_sayisi > 5`)
3. **6 aydır kullanılmayan kayıtlar** (`son_kullanim < bugun - 180 gun`)
4. **7 günden eski ajan mesajları** (`ajan_mesaj` tablosu)

## Cron'lar (toplam 5)
| Cron | Saat | Tip |
|:-----|:----:|:----|
| Self-improvement | 15dk | LLM |
| Memory backup | 00:30 | no_agent |
| Full backup | 03:00 | no_agent |
| DB temizlik | 04:00 | no_agent |
| Skill 5N1K | 05:00 | no_agent |
