---
name: autonomous-ai-agents_reymen-ogrenme-sistemi_references_stratejik-ajan-secici
description: Stratejik Ajan Seçici (stratejik_ajan_sec)
title: "Autonomous Ai Agents Reymen Ogrenme Sistemi References Stratejik Ajan Secici"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Stratejik Ajan Seçici (stratejik_ajan_sec) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Stratejik Ajan Seçici (stratejik_ajan_sec)

Reymen'de hata tipine göre anında persona/ajan değiştirme sistemi.

## Dosya

`akilli_yonlendirici.py` — `stratejik_ajan_sec()` fonksiyonu + 5 ajan personası

## 5 Ajan Personası

| ID | Rol | Tanım | Ne Zaman |
|----|-----|-------|----------|
| `genel_cozucu` | Genel Mantık Uzmanı | Varsayılan, tüm görevler | Başlangıç, eşleşme yoksa |
| `kod_uzmani` | Python Hata Ayıklama Uzmanı | SyntaxError, TypeError, NameError, IndentationError, AttributeError, ImportError, ValueError, KeyError, Traceback | Kod hatalarında |
| `sistem_mimari` | Altyapı Entegrasyon Uzmanı | FileNotFoundError, ConnectionError, Timeout, PermissionError, API anahtarı hataları, bağlantı sorunları | Dosya/ağ/altyapı hatalarında |
| `guvenlik_uzmani` | Güvenlik Uzmanı | Authentication, Authorization, Forbidden, SSL, RateLimit | Yetki/güvenlik hatalarında |
| `veri_uzmani` | Veri Mühendisi | SQLite hataları, JSON/YAML parse, encoding, CSV, Unicode | Veri/dosya formatı hatalarında |

## main.py Entegrasyonu (Circuit Breaker)

Her turda `motor.calistir()` sonucu `[Hata]` içeriyorsa tetiklenir:

```python
# main.py satır ~776
if "[Hata]" in gozlem or "Hatasi]" in gozlem:
    ardisik_hata += 1
    # stratejik_ajan_sec çağrılır
    yeni_ajan = stratejik_ajan_sec(aktif_ajan_id, gozlem)
    if yeni_ajan != aktif_ajan_id:
        aktif_ajan_id = yeni_ajan
        # Yeni persona prompt'a enjekte edilir
        mesajlar.append({"role": "user",
            "content": f"[SISTEM]: Ajan degisti. Yeni rol:\n{_persona_talimati}\n\nBu yeni rolle cozume devam et."
        })
        ardisik_hata = 1  # Sıfırla
        continue
    # 3 ardışık hata → reflexion / circuit breaker
```

## Değişkenler

- `aktif_ajan_id = "genel_cozucu"` — döngü başında tanımlanır
- `ajan_degisti` — flag, gerekiyorsa diğer sistemlere bildirim

## Test

```python
from akilli_yonlendirici import stratejik_ajan_sec, ajan_talimatini_getir

stratejik_ajan_sec("genel_cozucu", "SyntaxError: invalid syntax")
# → "kod_uzmani"

stratejik_ajan_sec("genel_cozucu", "ConnectionError: timeout")
# → "sistem_mimari"

ajan_talimatini_getir("kod_uzmani")
# → "Sen kidemli bir Python yazilim muhendisligi..."
```

## Önemli

- LLM çağrısı YAPMAZ — kural tabanlı, milisaniyelerde karar verir
- Her hata deseni 4 kategoriden birine girer: kod / sistem / güvenlik / veri
- Eşleşme yoksa mevcut ajan korunur (genel_cozucu)
- 30+ hata deseni tanınır
