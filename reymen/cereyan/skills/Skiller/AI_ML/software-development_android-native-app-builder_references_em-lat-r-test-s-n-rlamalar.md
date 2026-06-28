---
name: software-development_android-native-app-builder_references_em-lat-r-test-s-n-rlamalar
description: Emülatör Test Sınırlamaları
title: "Software Development Android Native App Builder References Em Lat R Test S N Rlamalar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Emülatör Test Sınırlamaları |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Emülatör Test Sınırlamaları

- **Sanal mikrofon yok:** Google APIs sistem imajı (`google_apis;x86_64`) SpeechRecognizer'ı destekler ama varsayılan emülatörde sanal ses girişi yoktur. SpeechRecognizer `ERROR_NO_MATCH` veya `ERROR_SPEECH_TIMEOUT` ile döner, hiçbir callback (onResults/onPartialResults) ateşlenmez.
- **Gerçek test:** Fiziksel telefona yükle (USB hata ayıklama) veya emülatöre host mikrofondan ses yönlendirmesi yap.
- **Google servis kontrolü:** `adb shell pm list packages google` ile doğrula
