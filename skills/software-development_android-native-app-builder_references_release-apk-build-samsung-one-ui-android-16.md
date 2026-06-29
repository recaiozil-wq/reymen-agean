---
name: software-development_android-native-app-builder_references_release-apk-build-samsung-one-ui-android-16
description: Release APK Build (Samsung / One UI / Android 16+)
title: "Software Development Android Native App Builder References Release Apk Build Samsung One Ui Android 16"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Release APK Build (Samsung / One UI / Android 16+) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Release APK Build (Samsung / One UI / Android 16+)

Samsung One UI 8+ (Android 16+) cihazlarda debug APK'ler **Auto Blocker** tarafından engellenir. Çözüm: release imzalı APK oluştur.

### 1. Keystore Oluştur

```bash
"<java_jdk_yolu>/bin/keytool" -genkey -v \
  -keystore "<proje>/release.keystore" \
  -alias <app_alias> \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass <sifre> -keypass <sifre> \
  -dname "CN=Hermes, OU=Dev, O=Hermes, L=Unknown, ST=Unknown, C=TR"
```

JDK yolunu `which keytool` ile bul. Örn: `C:\Program Files\Microsoft\jdk-21.0.11.10-hotspot\bin\keytool`

### 2. build.gradle.kts'e SigningConfig Ekle

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("../release.keystore")
            storePassword = "<sifre>"
            keyAlias = "<alias>"
            keyPassword = "<sifre>"
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = false
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

**Pitfall:** `signingConfigs` bloğu `buildTypes` bloğundan ÖNCE tanımlanmalı.

### 3. Release APK Derle

```bash
cd <proje>
export ANDROID_HOME="/c/Users/<user>/AppData/Local/Android/Sdk"
./gradlew assembleRelease --no-daemon
```

### 4. APK Çıktısı

`app/build/outputs/apk/release/app-release.apk` (~4.7 MB, debug'dan küçük)
Desktop'a: `cp app/build/outputs/apk/release/app-release.apk /c/Users/<user>/Desktop/Uygulama-Release.apk`

### 5. Samsung One UI Özel Ayarları

Kullanıcıya şu adımları ilet (Telegram üzerinden):

1. **Ayarlar > Güvenlik > Auto Blocker > KAPAT** (en önemlisi)
2. **Ayarlar > Biyometri ve güvenlik > Bilinmeyen uygulamalar > Telegram > İzin ver**
3. Alternatif: **Ayarlar > Uygulamalar > Telegram > Özel izinler > Bilinmeyen uygulamaları yükle > İzin ver**

Release APK bu ayarlarla sorunsuz kurulur.
