---
name: software-development_reymen-motor-arac-ekleme_references_hata_cozucu
description: hata_cozucu.py — Referans
title: "Software Development Reymen Motor Arac Ekleme References Hata Cozucu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | hata_cozucu.py — Referans |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# hata_cozucu.py — Referans

**Dosya:** `C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\hata_cozucu.py`
**Boyut:** 560 satir, ~20 KB

## Bilesenler

### HataWatchdog
- `threading.Event` ile guvenli durdurma (`while not self._durdurma.is_set()`)
- `Event.wait(timeout=aralik)` — `time.sleep()` yerine, aninda kapatilabilir
- `mss` + `pytesseract` ile OCR (graceful degrade)
- `try/except` icinde `continue` YOK — hata sonrasi wait atlanmaz
- Temp dosya olusturmaz (bellekte isler)

### HataKoduUretici
- `HATA-0001` formatinda siradaki kodu `_sayaç.txt` ile hizli uret
- `.ReYMeN/hata_kodlari/` klasorune .md olarak kaydeder
- `cozum_ekle()` ile mevcut kayda cozum ekleyip durumu "cozuldu" yapar

### TerminalHataParser
- Regex ile PowerShell/cmd hata ciktisini ayiklar
- `\+` karakteri regex'te escape edilmeli (`\\+`)
- Sonuc: `{"hata_var": bool, "hata_sayisi": int, "hata_mesajlari": [], "ozet": str}`

### CozumUygulayici
- `HATA-XXXX` kodunu bul, dosyayi ac, eski/yeni ile patch uygula
- Satir numarasi da destekler
- Basarili olunca hata kaydini "cozuldu" yapar

## motor.py Entegrasyonu
- 5 arac: HATA_WATCH_BASLAT, HATA_WATCH_DURDUR, HATA_KOD_AL, TERMINAL_HATA_PARSE, COZUM_UYGULA
- Erken kontrol (Registry oncesi) ile calistir()'a eklendi
- TOOLSET_GRUPLARI "hata" grubunda
