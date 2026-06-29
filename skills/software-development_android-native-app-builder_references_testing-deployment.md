---
name: software-development_android-native-app-builder_references_testing-deployment
description: Testing & Deployment
title: "Software Development Android Native App Builder References Testing Deployment"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Testing & Deployment |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Testing & Deployment

APK build ettikten sonra test etmek için **CLI build tercih edilir** — Android Studio Gradle sync'i beklemekten daha hızlı ve güvenilirdir.

### A. CLI Build (Tercih Edilen)
```bash
cd <proje_dizini>
export ANDROID_HOME="/c/Users/<user>/AppData/Local/Android/Sdk"
./gradlew assembleDebug --no-daemon
