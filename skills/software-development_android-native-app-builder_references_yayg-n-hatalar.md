---
name: software-development_android-native-app-builder_references_yayg-n-hatalar
description: Yaygın Hatalar
title: "Software Development Android Native App Builder References Yayg N Hatalar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Yaygın Hatalar |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Yaygın Hatalar
| Hata | Çözüm |
|------|-------|
| `dependencyResolution` hatası | `dependencyResolutionManagement` olarak düzelt |
| `android.useAndroidX` | `gradle.properties`'e ekle |
| SDK license kabulü | `yes | sdkmanager --licenses` |
| build-tools versiyonu | Gradle otomatik eksik olanı indirir |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | İmza uyuşmazlığı — önce `adb uninstall com.package` yap, sonra tekrar `adb install` |
| `INSTALL_FAILED_ALREADY_EXISTS` | `adb install -r` ile yeniden dene (replace) |
