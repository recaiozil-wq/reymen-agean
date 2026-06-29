---
name: software-development_re-hermes-v3_references_livetranscribe-comparison-2026-06-12
description: LiveTranscribe APK Comparison — 2026-06-12
title: "Software Development Re Hermes V3 References Livetranscribe Comparison 2026 06 12"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | LiveTranscribe APK Comparison — 2026-06-12 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# LiveTranscribe APK Comparison — 2026-06-12

## Hedefler

Dört APK karşılaştırıldı: base.apk, LiveTranscribe_24h_v3.apk, LiveTranscribe_24h_v8.7.apk, monolithic.apk

## İki Gruba Ayrışma

### Grup 1 — base + v8.7 (🟢 Daha az riskli)
- Google imzalı (orijinal sertifika)
- ~21-24 MB, ~1685 dosya
- Native .so yok
- Token footprint: AccessibilityService×6, chmod×6, getDeviceId×1

### Grup 2 — v3 + monolithic (🔴 En tehlikeli)
- HERMES özel keystore ile imzalı (trojanize edilmiş)
- ~28-31 MB, **3412 dosya**
- **7 adet native .so** (AArch64, TensorFlow Lite JNI dahil)
- Token footprint (AYNI — familya aynı):
  - `getDeviceId` ×5 (gerçek: 1 adet, 4'ü TFLite `getDeviceIds`)
  - `chmod` ×7 (gerçek: 1 adet)
  - `curl` ×2 → **FALSE POSITIVE** (curly-bracket)
  - `ptrace` ×1 → **FALSE POSITIVE** (C++ sembol)
  - `GetProcAddress` ×1 → **FALSE POSITIVE** (eglGetProcAddress)
  - `AccessibilityService` ×6 — gerçek
  - `LoadLibrary` ×2 — gerçek
  - `RECORD_AUDIO` ×2 — gerçek
  - `setComponentEnabledSetting` ×2 — gerçek
  - `getLastKnownLocation` ×1 — gerçek
  - `loadClass` ×1 — gerçek

## Risk Skoru

| APK | Puan | Seviye |
|-----|------|--------|
| base | 6/15 | 🟡 ORTA |
| v8.7 | 6/15 | 🟡 ORTA |
| v3 | 14/15 | 🔴 KRITIK |
| monolithic | 14/15 | 🔴 KRITIK |

## Anahtar Gözlemler

1. v3 ve monolithic **aynı APK** — aynı dosya sayısı (3412), aynı token footprint, aynı HERMES imzası
2. v3 = 27.8MB, monolithic = 30.9MB farkı muhtemelen split APK merge artefaktı
3. DeepSeek AI her iki gruptaki APK'ları doğru teşhis etti: "Live Transcribe taklidi infostealer"
4. BIND_ACCESSIBILITY_SERVICE + RECORD_AUDIO + SYSTEM_ALERT_WINDOW kombinasyonu her dört APK'da da var — Live Transcribe'ın kendi izinleri
5. **Eklenen zararlı imza:** v3/monolithic'te HERMES.RSA/SF imzası (base'de Google imzası)
