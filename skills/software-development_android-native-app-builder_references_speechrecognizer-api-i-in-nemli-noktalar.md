---
name: software-development_android-native-app-builder_references_speechrecognizer-api-i-in-nemli-noktalar
description: SpeechRecognizer API için Önemli Noktalar
title: "Software Development Android Native App Builder References Speechrecognizer Api I In Nemli Noktalar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | SpeechRecognizer API için Önemli Noktalar |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## SpeechRecognizer API için Önemli Noktalar
- **İzin:** `RECORD_AUDIO` manifest'te + çalışma zamanında istenmeli
- **Intent extras:** `EXTRA_PARTIAL_RESULTS=true` (kısmi sonuç), `EXTRA_LANGUAGE_MODEL=FREE_FORM`
- **Sürekli dinleme:** `onResults()` callback'inde `startListening()`'i tekrar çağır
- **Hata yönetimi:** `onError()`'da otomatik yeniden başlatma
- **Pitfall:** SpeechRecognizer servisi destroy edilmezse memory leak; `onDestroy()`'da `speechRecognizer.destroy()` çağır
