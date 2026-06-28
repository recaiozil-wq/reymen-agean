---
name: ortak-bilgi-deposu_references_ajan-iletisim-protokolu
description: Ajan İletişim Protokolü — ReYMeN Inter-Agent v1
title: "Ortak Bilgi Deposu References Ajan Iletisim Protokolu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Ajan İletişim Protokolü — ReYMeN Inter-Agent v1 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Ajan İletişim Protokolü — ReYMeN Inter-Agent v1

## 3 Ajan
- 🐉 Kali: `kali/network/nmap`, `kali/web`, `kali/network`
- 🪟 Windows: `windows/terminal/network`, `windows/terminal/system`
- 🤖 Hermes: `kullanici/profil`, `sistem/mimari`, `sistem/pitfall`

## Paylaşımlı Yapı
```
hermes_projesi/
├── reymen/cereyan/.ReYMeN/ogrenmeler.db  ← ORTAK DB
├── reymen/cereyan/skills/{kategori}/{adi}.md  ← SKILL'ler
├── .ReYMeN/decisions.md                      ← KARAR'lar
└── .ReYMeN/kazanimlar.md                     ← KAZANIM log'ları (tüm ajanlar yazar)
```

## Mesaj Formatı
```json
{"kaynak": "kali|windows|cad", "komut": "PORT_BLOCK|SCAN|ERROR", "port": 1234}
```

## Garantiler
- Timeout: 30sn
- ACK zorunlu
- Retry: max 3
- Heartbeat: 30sn'de bir
- Circuit breaker: 3 hata → kalıcı dur
