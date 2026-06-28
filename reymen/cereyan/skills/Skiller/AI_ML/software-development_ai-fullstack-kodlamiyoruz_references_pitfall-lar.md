---
name: software-development_ai-fullstack-kodlamiyoruz_references_pitfall-lar
description: PITFALL'LAR
title: "Software Development Ai Fullstack Kodlamiyoruz References Pitfall Lar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | PITFALL'LAR |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## PITFALL'LAR

- **Context sıfırlanması**: AI ajanı 1M token'da context kaybeder. Memory.md ile çöz.
- **Railway credential'ları**: Environment variable'ları Railway dashboard'dan ayarla, `.env`'e yazma.
- **R2 CORS**: Frontend'den direkt yükleme yapacaksan CORS ayarlarını unutma.
- **Test coverage düşüklüğü**: AI bazen test yazmayı atlar. "Test yaz" diye zorla.
- **Deployment hataları**: Railway CLI login'inin hala aktif olduğunu kontrol et.
- **Rate limiting**: Free tier AI modelleri (OpenRouter free) 429 dönebilir. Fallback chain kullan.
