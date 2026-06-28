---
name: session-aware-qa
description: Kullanıcı sorusu gelir
title: Session Aware Qa
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

# Session Bilinçli QA

## Akış

```
Kullanıcı sorusu gelir
  ↓
session_search(query, limit=3)
  ├─ Bulundu (benzer soru+cevap)
  │   → "Bu soruyu daha önce sormuştun. [önceki cevap]"
  └─ Bulunamadı
      → normal LLM akışı
```

## Kurallar

1. Kimlik/model sorularında (`sen kimsin?`, `hangi modelsin?`) her zaman AYNI cevap ver
2. Bulunan cevabı teyit için tekrar LLM'e sorma — direkt hafızadan döndür
3. session_search'te tam eşleşme yoksa keyword benzerliği de dene
