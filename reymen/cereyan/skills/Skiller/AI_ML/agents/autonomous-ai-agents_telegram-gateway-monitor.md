---
name: telegram-gateway-monitor
description: >
  Bağlantı 30 dakikada bir kontrol edilir, test mesajı gönderilir,
  hata alınırsa otomatik onarım adımları uygulanır ve sonuç kaydedilir.
  Hedef listeleme ve gönderme için `hermes send --list` + `hermes send --to <target>` kullanılır.
title: "Telegram Gateway Monitor"
version: 1.2.0
author: marko
license: MIT
metadata:
  hermes:
    tags: [telegram, gateway, monitor, watchdog, reconnect]
category: autonomous-ai-agents
audience: user
tags: [agents, ai, automation, telegram, tor]
related_skills: [hermes-agent]


---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Otonom ajan geliştiricisi |
| **Ne?** | Bağlantı 30 dakikada bir kontrol edilir, test mesajı gönderilir, hata alınırsa otomatik onarım adımları uygulanır ve sonuç kaydedilir. Hedef listeleme ve gönderme için `hermes send --list` + `hermes s |
| **Nerede?** | AI_ML/agents/ |
| **Ne Zaman?** | ilgili görev gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |


# Telegram Gateway Monitor

Bu skill modüler bir yönlendiricidir. İhtiyacınız olan bölümü seçin ve ilgili reference dosyasını yükleyin.

## 📂 Bölümler

| Bölüm | Reference Dosyası |
|-------|------------------|
| Kural | `references/kural.md` |
| gateway_state.json Kirlenmesi (test run'ları state'i bozduğunda) | `references/gateway-state-json-corruption.md` |
| Hermes CLI Invocation (PYTHONPATH fix) | `references/hermes-cli-invocation.md` |
| Yeni Bot Token'ı ile Tam Sıfırlama Akışı | `references/yeni-bot-token-ile-tam-s-f-rlama-ak.md` |
| Zorunlu adımlar | `references/zorunlu-ad-mlar.md` |
| Telegram test mesajı içeriği | `references/telegram-test-mesaj-i-eri-i.md` |
| Pitfall | `references/pitfall.md` |
| send_message Tool Token Cache | `references/send_message-tool-token-cache.md` |
| Kazanımlar / Operasyon Notları (sessiz ve güvenli kullanım için) | `references/kazan-mlar-operasyon-notlar-sessiz-ve-g-venli-kullan-m-i-in.md` |
| Polling Sağlık Kontrolü — sessiz donma tespiti ve çözümü | `references/polling-saglik-kontrolu.md` |
| Not | `references/not.md` |
| Cron Teslimat Davranışı (cron job'da `hermes send` atlanır) | `references/cron-teslimat-davranisi.md` |
| .env kalıcılığı kuralı | `references/env-kal-c-l-kural.md` |
| Obsidian kayıt | `references/obsidian-kay-t.md` |

## Kullanım

1. İhtiyacın olan bölümü belirle
2. `skill_view(name="...", file_path="references/...")` ile yükle
