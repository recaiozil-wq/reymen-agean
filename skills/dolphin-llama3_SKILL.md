---
name: dolphin-llama3
description: '- Model: `dolphin-llama3`'
title: Dolphin Llama3
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

# Dolphin Llama3 Yönlendirme

- Model: `dolphin-llama3`
- Ana akış: `stepfun/step-3.7-flash:free`
- Reddit-benzeri görevler için `dolphin-llama3` kullan.
- Dolphin-llama3 görev bitince tekrar `stepfun/step-3.7-flash:free` (mevcut ana akış) moduna geç.
- Kullanıcı her görevde ilk adım olarak Hermes skill + Obsidian kontrolü yap.
- Eğer kayıt varsa yeniden yazmadan ilerle.
- Kullanıcı onayı verdiğinde görev, ilgili skill + Obsidian’a kaydedilir.

## Kullanım
1. Görevde kullanılacak modeli buradan belirle: reddit gibi yönler için `dolphin-llama3`, ana akış için `stepfun/step-3.7-flash:free`.
2. Görev tamamlandıktan sonra akışı ana modele (`stepfun/step-3.7-flash:free`) geri ver.
