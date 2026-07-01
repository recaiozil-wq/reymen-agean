# Karar Kaydı — Proaktif Bakım Sistemi

**Tarih:** 2026-07-01 22:45

## Ne yapıldı?
8 maddeli proaktif bakım sistemi kuruldu — ReYMeN Agent'a kalıcı entegre.

## Neden?
3 bot'un aynı soruya farklı cevap vermesi, config drift, gateway çökmeleri, memory farklılıkları gibi sorunların tekrarlanmasını engellemek için.

## Yapılanlar

| # | Önlem | Dosya | Durum |
|---|-------|-------|-------|
| 1 | **Config drift dedektörü** | proaktif_bakim.py | ✅ |
| 2 | **Gateway watchdog (3 profil)** | proaktif_bakim.py | ✅ |
| 3 | **SOUL.md master sync** | proaktif_bakim.py → 3 profil güncellendi | ✅ |
| 4 | **state.db prune (30 gün)** | proaktif_bakim.py | ✅ |
| 5 | **MEMORY.md sync** | proaktif_bakim.py | ✅ |
| 6 | **Haftalık rapor (Pazar)** | proaktif_bakim.py | ✅ |
| 7 | **Config template doğrulama** | proaktif_bakim.py | ✅ |
| 8 | **Gateway health kontrol** | proaktif_bakim.py | ✅ |

## Cron job'lar
- `proaktif-bakim` — her 30dk (no_agent=True, sessiz)
- `kiral38-watchdog` — her 5dk (no_agent=True, sessiz)

## Test bulguları
- default: gateway.pid YOK → restart gönderildi ✅
- reymen/kiral38: state güncel değil (beklenen, gateway 409 döngüsünde)
- SOUL.md: 3 profil de güncellendi ✅

## Alternatifler
- Ayrı ayrı 8 cron job (red — tek script daha verimli)
- Manuel bakım (red — otonom olmalı)
