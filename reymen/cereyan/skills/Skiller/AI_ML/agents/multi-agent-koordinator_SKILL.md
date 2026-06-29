--- 
title: Çoklu Ajan Koordinatörü
name: multi-agent-koordinator
description: Birden çok ReYMeN ajanının görev dağılımı, mesajlaşma ve senkronizasyonunu yönetir
tags: [agent, koordinasyon, mesajlasma, orkestrasyon]
---

# Çoklu Ajan Koordinatörü

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Birden çok ajanın görev dağılımını, aralarındaki mesajlaşmayı ve senkronizasyonu yönetir |
| Nerede | reymen/cereyan/skills/Skiller/AI_ML/agents/ |
| Ne Zaman | 2'den fazla ajan aynı projede çalışırken |
| Neden | Ajanların birbirinin işine karışmadan, çakışma olmadan paralel çalışması için |
| Nasıl | Master ajan belirlenir, görevler payload olarak dağıtılır, sonuçlar toplanır |

## Görev Dağıtım Protokolü

1. **Master Ajan** — Koordinasyonu yönetir, görevleri böler ve dağıtır
2. **Worker Ajan** — Kendine atanan görevi yürütür, sonucu master'a iletir
3. **Queue Sistemi** — Görevler FIFO kuyrukta bekler, her worker bir sonraki görevi alır

## Mesajlaşma Formatı

```json
{"from": "kali-agent", "to": "windows-agent", "cmd": "BLOCK_PORT",
 "payload": {"port": 4444, "protocol": "tcp"}, "reply_to": "kali-agent"}
```

## Çakışma Önleme

- Aynı dosyaya iki ajan yazamaz — lock mekanizması
- Aynı porta iki ajan tarama yapamaz — port havuzu
- Aynı tool'u iki ajan aynı anda kullanamaz — semafor
