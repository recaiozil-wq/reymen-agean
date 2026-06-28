---
name: software-development_ai-fullstack-kodlamiyoruz_references_ai-ajan-ali-ma-d-ng-s
description: AI AJAN ÇALIŞMA DÖNGÜSÜ
title: "Software Development Ai Fullstack Kodlamiyoruz References Ai Ajan Ali Ma D Ng S"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | AI AJAN ÇALIŞMA DÖNGÜSÜ |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## AI AJAN ÇALIŞMA DÖNGÜSÜ

### 1. Sprint/Issue Yapısı
AI ajanı GitHub'da milestone'lar ve issue'lar açsın:

```
Milestone 0 → Infrastructure (DB, Redis, deployment)
Milestone 0.5 → Auth (giriş, kayıt, oturum)
Milestone 1 → Feed (ana akış, gönderi listeleme)
Milestone 2 → Post Creation (içerik oluşturma/editör)
...
```

### 2. Her Sprint'te
1. Issue'ları oluştur (açıklama + task list + gerekirse görsel)
2. Her issue'yu branch açıp çöz
3. Test yaz (Playwright)
4. Commit → `git commit -m "feat: #12 post editor"`
5. Deploy → dev ortamına
6. Screenshot al
7. Kontrol et → sorun yoksa merge

### 3. Context Yönetimi
AI ajanının memory'si sıfırlandığında:
```
📁 memory.md dosyası oluştur:
- Alınan kararlar
- Tamamlanan issue'lar
- Bekleyen işler
- Stack/teknoloji seçimleri
```

Her yeni session'da:
```
📖 memory.md'yi oku
📋 Kaldığın issue'dan devam et
```
