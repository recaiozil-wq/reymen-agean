---
skill_id: 30b3a2b7474c
usage_count: 1
last_used: 2026-06-16
---
## send_message Tool Token Cache

`send_message` tool'u, gateway'den **bağımsız** olarak kendi token cache'ine sahiptir. Oturum başlangıcında `.env`'yi okur ve tüm oturum boyunca aynı token'ı kullanır. Gateway restart (`--replace`) bu cache'i etkilemez.

**Belirti:** Gateway "connected", direkt API çalışıyor, ama `send_message` "bot was blocked" hatası veriyor.

**Tanı ve çözüm:** `references/send_message-token-cache.md`

**Acil durum scripti:** `scripts/send_tg.py` — direkt Python API çağrısı yapar, `send_message` cache'ini bypass eder.