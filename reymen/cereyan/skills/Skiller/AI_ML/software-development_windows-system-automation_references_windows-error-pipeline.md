---
name: software-development_windows-system-automation_references_windows-error-pipeline
description: Windows Error Handling Pipeline (Planlı)
title: "Software Development Windows System Automation References Windows Error Pipeline"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Windows Error Handling Pipeline (Planlı) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Windows Error Handling Pipeline (Planlı)

## Ne İşe Yarar

Windows'ta hata çıktığında (ekran dialog'u, terminal çıktısı, uygulama crash'i):
1. Hatayı **otomatik tespit et** (ekran OCR + terminal parse)
2. **Sınıflandır** ve **çözüm öner** veya **hata kodu** üret
3. Kullanıcı Claude'a hata kodunu verip **çözüm alır**
4. Çözümü **otomatik uygula**

## Mimari — 4 Bileşen

### 1. HataWatchdog — Ekran Hatası İzleyici

```
threading.Thread + Event ile sürekli döngü
  → mss ile screenshot (belirli aralık, örn: 5sn)
  → OCR ile hata kelimeleri tara: "Hata", "Error", "Exception", "Access Denied"
  → Bulunca callback tetikle → HataKoduUretici'ye gönder
  → Event.set() ile durdurulabilir
```

**Teknik:**
- `mss` (hızlı screenshot, PIL gerektirmez)
- `pytesseract` veya `easyocr` (try/except, graceful degrade)
- Regex: `Hata|Error|Exception|Access.?Denied|File.?Not.?Found|critical|failure`
- `threading.Event` ile `durdur()` metodu

### 2. HataKoduUretici — Claude İçin Hata Kodu

```
Hata metni + kategori + ekran görüntüsü → HATA-{sayı}: {kategori}: {özet}
  → .ReYMeN/hata_kodlari/HATA-{sayı}.md olarak kaydet
  → İçerik:
    - Hata kodu: HATA-XXXX
    - Zaman: ISO-8601
    - Ekran görüntüsü: path
    - Hata metni: raw OCR çıktısı
    - Kategori: import/syntax/tip/dizin/network/bilinmeyen
    - Çözüm durumu: cozulmedi → cozuldu → bekliyor
```

### 3. TerminalHataParser — Windows Terminal Çıktısı

```
PowerShell/cmd çıktısını al → regex ile hata satırlarını ayıkla
  → Kalıplar:
    - PowerShell: "Hata:", "Error:", "Exception:", "failed:"
    - cmd: "hatalı", "tanınmıyor", "AccessDenied", "dosya bulunamadı"
    - pip: "ERROR:", "Could not install"
    - git: "fatal:", "error:", "failed to"
  → Çıktı: {hata_var_mi: bool, satirlar: [...], kategori: str, ozet: str}
```

### 4. CozumUygulayici — Kullanıcı Çözümünü Uygula

```
Kullanıcı "HATA-XXXX: <çözüm metni>" gönderir
  → .ReYMeN/hata_kodlari/HATA-XXXX.md'yi bul
  → Durumu "cozuldu" yap, çözüm metnini ekle
  → Çözüm içinde patch/dosya değişikliği varsa uygula:
    - "Dosya: X" → patch uygula
    - "Komut: Y" → terminal'de çalıştır
    - "Kurulum: Z" → pip/install çalıştır
```

## motor.py'ye Eklenecek Araçlar

```
HATA_WATCH_BASLAT(saniye=5)    → Watchdog'u başlat
HATA_WATCH_DURDUR              → Watchdog'u durdur
HATA_KOD_AL(hata_metni)        → Hata kodu üret, döndür
TERMINAL_HATA_PARSE(cikti)     → Terminal çıktısını parse et
COZUM_UYGULA(hata_kodu, cozum) → Çözümü uygula
```

## Teknik Kurallar

- `from __future__ import annotations`
- Tüm import'lar try/except ile (graceful degrade)
- `print()` yerine `logging`
- `pathlib.Path` ile Windows path'leri
- Türkçe değişken/fonksiyon adları
- Her sınıfın `__main__` test bloğu
- `.ReYMeN/hata_kodlari/` klasörü (atomik yazma: temp+rename)

## Durum

⚠️ **Plan aşamasında** — hata_cozucu.py henüz yazılmadı.
Kullanıcı Claude Code'a yazdıracak, çözümü alıp entegre edilecek.
