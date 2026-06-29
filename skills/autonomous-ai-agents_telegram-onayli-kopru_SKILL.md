---
name: autonomous-ai-agents-telegram-onayli-kopru
description: Claude + Ollama (Dolphin) arasında dosya tabanlı köprü. Telegram üzerinden
  onay mekanizması ile çalışır.
title: Autonomous Ai Agents Telegram Onayli Kopru
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

# Telegram Onaylı Köprü

Claude + Ollama (Dolphin) arasında dosya tabanlı köprü. Telegram üzerinden onay mekanizması ile çalışır.

## Kullanım

1. `python bridge_tg.py` çalıştır
2. Hermes `bridge_status.txt` okur, Telegram'a aktarır
3. Kullanıcı `devam` / `dur` der, Hermes `bridge_signal.txt`'e yazar

## Güvenlik

- `MAX_TURN=5` — maksimum 5 tur
- `300sn timeout` — otomatik durma
- Dosya tabanlı sinyalizasyon

## Akış

1. Kullanıcı Telegram'dan komut gönderir
2. Hermes köprü script'ini çalıştırır
3. Script Claude + Ollama arasında gidiş-geliş yapar
4. Her turda durumu `bridge_status.txt`'ye yazar
5. Hermes durumu okur ve Telegram'a iletir
6. Kullanıcı onay verene kadar veya timeout'a kadar devam eder

## Log Örneği

```
# Tur 1 Claude
def tek_sayilari_topla(liste):
    return sum(x for x in liste if x % 2 != 0)

# Tur 1 Ollama (Dolphin)
Dolphin: Hello Claude! I'm here to help you...
```
