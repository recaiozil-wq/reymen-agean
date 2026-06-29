--- 
title: Ajan Kendini İzleme ve Sağlık Kontrolü
name: agent-kendini-izleme
description: ReYMeN ajanlarının performans, hata oranı, bellek kullanımı ve yaşam sinyallerini izler
tags: [agent, izleme, saglik, performans, monitor]
---

# Ajan Kendini İzleme ve Sağlık Kontrolü

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Ajanların CPU/RAM kullanımı, hata oranı, yanıt süresi ve yaşam sinyallerini izler |
| Nerede | reymen/cereyan/skills/Skiller/AI_ML/agents/ |
| Ne Zaman | Ajan yavaşladığında, hata verdiğinde veya periyodik bakımda |
| Neden | Ajanın sağlıklı çalıştığından emin olmak ve sorunları erken tespit etmek için |
| Nasıl | 30sn'de bir heartbeat sinyali, hata sayaçları ve threshold kontrolleri ile |

## İzleme Metrikleri

| Metrik | Eşik | Aksiyon |
|--------|------|---------|
| Heartbeat | >90sn sessiz | Ajanı yeniden başlat |
| Hata Oranı | >%20 son 10 çağrı | Circuit breaker devreye al |
| Yanıt Süresi | >30sn ortalama | LLM modelini küçült |
| Bellek | >%80 kullanım | Cache temizle |

## Kurtarma Adımları

1. Heartbeat kaçtı → process listele, varsa kill, yeniden spawn
2. Hata oranı yüksek → retry mekanizmasını devre dışı bırak, kullanıcıya bildir
3. Bellek şişti → `hafiza.temizle()` ile bayat kayıtları sil
