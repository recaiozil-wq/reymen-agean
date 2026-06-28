---
name: autonomous-ai-agents_telegram-gateway-monitor_references_send_message-tool-token-cache
description: send_message Tool Token Cache
title: "Autonomous Ai Agents Telegram Gateway Monitor References Send Message Tool Token Cache"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | send_message Tool Token Cache |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## send_message Tool Token Cache

`send_message` tool'u, gateway'den **bağımsız** olarak kendi token cache'ine sahiptir. Oturum başlangıcında `.env`'yi okur ve tüm oturum boyunca aynı token'ı kullanır. Gateway restart (`--replace`) bu cache'i etkilemez.

**Belirti:** Gateway "connected", direkt API çalışıyor, ama `send_message` "bot was blocked" hatası veriyor.

**Tanı ve çözüm:** `references/send_message-token-cache.md`

**Acil durum scripti:** `scripts/send_tg.py` — direkt Python API çağrısı yapar, `send_message` cache'ini bypass eder.
