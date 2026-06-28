---
name: software-development_android-native-app-builder_references_apk-n-n-ge-erli-oldu-unu-kontrol-et
description: APK'nın geçerli olduğunu kontrol et
title: "Software Development Android Native App Builder References Apk N N Ge Erli Oldu Unu Kontrol Et"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | APK'nın geçerli olduğunu kontrol et |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# APK'nın geçerli olduğunu kontrol et
/path/to/build-tools/35.0.1/aapt2 dump badging "C:\\Users\\marko\\Desktop\\Uygulama.apk" | grep -E "^package:|minSdkVersion:|targetSdkVersion:|native-code:"
```

- `native-code:` satırı yoksa → APK saf Java/Kotlin, tüm mimarilerde çalışır
- `native-code: armeabi-v7a` gibi bir satır varsa → sadece ARM cihazlarda çalışır
- Debug APK'ler Play Store'dan değil, manuel kurulum içindir — bu normaldir
