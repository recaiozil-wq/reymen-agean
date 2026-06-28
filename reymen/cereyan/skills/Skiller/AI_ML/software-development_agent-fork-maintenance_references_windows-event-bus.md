---
name: software-development_agent-fork-maintenance_references_windows-event-bus
description: Windows Automation Event Bus — Reference Architecture
title: "Software Development Agent Fork Maintenance References Windows Event Bus"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Windows Automation Event Bus — Reference Architecture |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Windows Automation Event Bus — Reference Architecture

## Problem

Windows automation modules (`hata_cozucu.py`, `tor_otomasyonu.py`, `araclar_nisan.py`, `cokus_raporlayici.py`, `akilli_yonlendirici.py`) were independent — each caught errors or found targets but never notified the others. A Tor timeout didn't trigger the error watchdog; a found target didn't auto-navigate.

## Solution: Central Event Bus

`WindowsEventBus` (in `windows_events.py`) is a singleton, thread-safe pub/sub system.

```
┌─────────────────────────────────────────────────────────┐
│                    WindowsEventBus                       │
│  dinle(tip, fn)   yayinla(tip, data)   son_olaylar(N)   │
└────┬──────────┬──────────┬──────────┬───────────────────┘
     │          │          │          │
┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌──▼────────┐
│ hata_  │ │ tor_   │ │ araclar_│ │ cokus_    │
│ cozucu │ │otomasyon│ │ nisan   │ │ raporlayici│
└────────┘ └────────┘ └────────┘ └───────────┘
```

## Event Types

| Constant | Fired When | Payload | Auto-Listeners |
|----------|-----------|---------|---------------|
| `OLAY_HATA` | Any module catches an error | `{mesaj, hata_sayisi, kaynak}` | `cokus_raporlayici` (3+ errors → crash report) |
| `OLAY_NISAN` | Target/pattern found | `{hedef, url, konum}` | `tor_otomasyonu` (navigate to target) |
| `OLAY_TOR_HATA` | Tor browser operation fails | `{mesaj, kaynak}` | `hata_cozucu` (attempt auto-fix) |
| `OLAY_COKUS` | Irrecoverable crash | `{gorev, rapor}` | User notification |
| `OLAY_TOR_BASARILI` | Tor operation succeeds | `{adim, sure_sn}` | `akilli_yonlendirici` (log) |
| `OLAY_COZUM_UYGULANDI` | Auto-fix applied | `{cozum, kaynak}` | `motor.py` (log) |
| `OLAY_SISTEM_UYARI` | Non-critical warning | `{mesaj, seviye}` | All modules (log) |

## Integration Wiring

`windows_entegrasyon.windows_entegrasyonu_baslat()` does:

```python
bus = event_bus_al()

# 1. Tor error → hata_cozucu
cozum = CozumUygulayici()
bus.dinle(OLAY_TOR_HATA, lambda v: cozum.cozum_uygula(v.get("mesaj","")))

# 2. Target found → tor_otomasyonu
tor = TorNavigator()
bus.dinle(OLAY_NISAN, lambda v: tor.git(v.get("hedef","")))

# 3. Error count → crash report
bus.dinle(OLAY_HATA, lambda v: cokus_raporu_uret(...) if v["hata_sayisi"] >= 3)

# 4. Tor success → log
bus.dinle(OLAY_TOR_BASARILI, lambda v: print(f"✅ {v['adim']}"))

# 5. Fix applied → log
bus.dinle(OLAY_COZUM_UYGULANDI, lambda v: print(f"🔧 {v['cozum']}"))
```

## Thread Safety

- All state mutations (`_dinleyiciler`, `_gecmis`) are guarded by `threading.Lock`
- Listener dispatch happens OUTSIDE the lock to prevent deadlocks
- History is bounded at 100 events (FIFO)

## Graceful Degradation

Each module import is wrapped in try/except. If `hata_cozucu.py` is missing, the Tor error → auto-fix pipeline simply doesn't register; the rest of the system continues normally.
