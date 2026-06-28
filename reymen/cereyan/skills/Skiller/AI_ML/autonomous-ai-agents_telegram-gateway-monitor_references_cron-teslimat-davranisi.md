---
name: autonomous-ai-agents_telegram-gateway-monitor_references_cron-teslimat-davranisi
description: Cron Teslimat Davranışı
title: "Autonomous Ai Agents Telegram Gateway Monitor References Cron Teslimat Davranisi"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Cron Teslimat Davranışı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Cron Teslimat Davranışı

### Temel Kural

Bu skill cron job olarak çalıştırıldığında (30 dakikada bir), **`hermes send --to` ile test mesajı gönderilemez.** Sistem şu yanıtı verir:

```
Skipped send_message to telegram:6328823909. This cron job will already auto-deliver
its final response to that same target. Put the intended user-facing content in your
final response instead, or use a different target if you want an additional message.
```

### Neden?

Cron job otomasyonu, agent'ın **final response**'unu otomatik olarak hedefe (Telegram) iletir. Bu nedenle ayrıca `hermes send` çağırmak gereksizdir ve sistem tarafından engellenir.

### Pratik Etki

| Durum | Ne Olur |
|-------|---------|
| `hermes send --to "telegram:Q !" "test mesajı"` | ⛔ Atlanır (Skipped) |
| Final response (bu metin) | ✅ Otomatik iletilir |

### Monitor Turu İçin Adımlar

1. **Test mesajı göndermeye çalışma** — çalışmaz, atlanır.
2. **Raporunu final response olarak yaz** — bu metin kullanıcıya gider.
3. **Obsidian'a log kaydı yap** (`mcp_obsidian_vault_append`) — ayrı bir kanalda kalıcı kayıt için.
4. Final response'un kullanıcıya ulaşacağını varsayarak çalış.

### Hata Durumunda

Eğer bağlantı sorunu varsa ve cron teslimatı da çalışmıyorsa:
- Obsidian log'u yine de yaz (en azından kalıcı kayıt kalsın)
- Kullanıcı bir sonraki kontrol turunda durumu görür
- Alternatif: normal (cron olmayan) bir oturumda `hermes send` ile manuel test yapılabilir
