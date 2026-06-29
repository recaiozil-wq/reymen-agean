---
name: software-development_android-native-app-builder_references_gradlew-indir
description: gradlew indir
title: "Software Development Android Native App Builder References Gradlew Indir"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | gradlew indir |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# gradlew indir
curl -sL "https://raw.githubusercontent.com/gradle/gradle/v8.11.1/gradlew" -o gradlew
curl -sL "https://raw.githubusercontent.com/gradle/gradle/v8.11.1/gradlew.bat" -o gradlew.bat
chmod +x gradlew gradlew.bat
```

### 3. Build
```bash
export ANDROID_HOME="/c/Users/<user>/AppData/Local/Android/Sdk"
export ANDROID_SDK_ROOT="/c/Users/<user>/AppData/Local/Android/Sdk"
./gradlew assembleDebug --no-daemon
```

### 4. APK konumu
`app/build/outputs/apk/debug/app-debug.apk`
