---
name: software-development_reymen-tool-patterns_references_hata-cozucu-arch
description: hata_cozucu.py — 4 Bileşenli Hata Yönetimi Mimarisi
title: "Software Development Reymen Tool Patterns References Hata Cozucu Arch"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | hata_cozucu.py — 4 Bileşenli Hata Yönetimi Mimarisi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# hata_cozucu.py — 4 Bileşenli Hata Yönetimi Mimarisi

Bu dosya, `hata_cozucu.py` modülünün mimarisini ve `motor.py`'ye entegrasyonunu açıklar.

## Genel Bakış

```
Kullanıcı/LLM
  │
  ├── HATA_WATCH_BASLAT/DURDUR
  │     └── HataWatchdog: threading ile ekranı tara, OCR ile hata bul
  │
  ├── HATA_KOD_AL
  │     └── HataKoduUretici: HATA-XXXX kodla, .md olarak kaydet
  │
  ├── TERMINAL_HATA_PARSE
  │     └── TerminalHataParser: stdout/stderr'den regex ile hata ayıkla
  │
  └── COZUM_UYGULA
        └── CozumUygulayici: Claude'dan gelen çözümü dosyaya patch uygula
              └── HataKoduUretici.cozum_ekle() — kaydı "çözüldü" yap
```

## Dosya Yapısı

```
.ReYMeN/hata_kodlari/
├── _sayaç.txt          ← HATA-0001, HATA-0002... sayacı
├── HATA-0001.md        ← Hata kaydı (frontmatter + detay)
├── HATA-0002.md
└── ...
```

## Bileşen Detayları

### 1. HataWatchdog

```python
watchdog = HataWatchdog(aralik_sn=5.0)
watchdog.baslat()   # threading.Thread ile arka planda başla
watchdog.durdur()   # threading.Event.set() ile durdur
```

- **Bağımlılık:** mss (ekran görüntüsü), pytesseract (OCR), PIL
- **Graceful degrade:** Modüller yoksa watchdog çalışır ama hiçbir şey yapmaz
- **Anahtar kelimeler:** `error`, `hata`, `exception`, `access denied`, `file not found`
- **Callback:** Hata bulunca `callback(ekran_metni, eslesen_kelimeler)` tetikler

### 2. HataKoduUretici

```python
uretici = HataKoduUretici()
kayit = uretici.kaydet(hata_metni, ekran_yolu="...", dosya="...", satir=0)
# -> HataKaydi(kod="HATA-0001", kategori="import", ozet="...")

uretici.cozum_ekle("HATA-0001", "çözüm açıklaması")  # durum → "cozuldu"
```

- **Kategori tespiti:** 7 regex (import, syntax, tip, dosya, baglanti, bellek, ekran)
- **Sayaç:** Dosya tabanlı (`_sayaç.txt`) — oturumlar arası kalıcı
- **Çıktı:** YAML frontmatter'lı .md dosyası (kod, zaman, kategori, durum)

### 3. TerminalHataParser

```python
parser = TerminalHataParser()
sonuc = parser.parse(terminal_ciktisi)
# -> {"hata_var": bool, "hata_sayisi": int, "hata_mesajlari": [...], "ozet": str}
```

- **Regex kalıpları:** `(?:Hata|Error|ERROR)\s*[:：]\s*(.+)`, Traceback, PowerShell ErrorId
- **İkili colon:** Hem `:` (ASCII) hem `：` (full-width Türkçe) kapsanır
- **PS ek:** `+ CategoryInfo`, `+ FullyQualifiedErrorId` için özel desenler

### 4. CozumUygulayici

```python
cozum = CozumUygulayici(hata_uretici)
sonuc = cozum.uygula("""HATA-0001:
Dosya: test.py
Satir: 10
Eski: hatali_kod()
Yeni: dogru_kod()
""")
# -> {"basarili": bool, "patch_sonuc": str, "kod": "HATA-0001"}
```

- **Çözüm formatı:** `HATA-XXXX:\nDosya: ...\nSatir: N\nEski: ...\nYeni: ...`
- **Patch stratejisi:** Önce `Eski` metnini dosyada ara, bulamazsa `Satir` bazlı değiştir
- **Hata kaydı güncelleme:** Başarılı patch sonrası `.ReYMeN/hata_kodlari/HATA-XXXX.md`'de durum "çözüldü" yapılır

## motor.py Entegrasyonu (3 Adım)

### Adım 1: TOOLSET_GRUPLARI

```python
TOOLSET_GRUPLARI = {
    ...
    "hata": {"HATA_WATCH_BASLAT", "HATA_WATCH_DURDUR", "HATA_KOD_AL",
             "TERMINAL_HATA_PARSE", "COZUM_UYGULA"},
}
```

### Adım 2: _DURUM_MESAJLARI

```python
_DURUM_MESAJLARI = {
    ...
    "HATA_WATCH_BASLAT":  "Hata watchdog baslatiliyor...",
    "HATA_KOD_AL":        "Hata kodu aliniyor...",
    "TERMINAL_HATA_PARSE": "Terminal ciktisi taranıyor...",
    "COZUM_UYGULA":       "Cozum uygulaniyor...",
}
```

### Adım 3: calistir()'a Erken Kontrol

Registry/Plugin kontrollerinden **önce** eklenir. Detaylı kod için `reymen-tool-patterns` skilindeki "Yöntem 2" bölümüne bak.

## Kodlama Kuralları (Bu Modül İçin)

```python
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

# Opsiyonel bağımlılıklar: try/except ile import et
try:
    import mss as _mss
    _MSS_VAR = True
except ImportError:
    _MSS_VAR = False

# print() yerine logging kullan
logger.info("[HataWatchdog] Baslatildi.")
logger.error("[HataKod] Kayit hatasi: %s", e)

# Windows path'leri icin pathlib.Path
HATA_KLASORU = ROOT / ".ReYMeN" / "hata_kodlari"

# Regex'teki `+` karakterini escape et: r"\+" (r"+" hata verir)
```
