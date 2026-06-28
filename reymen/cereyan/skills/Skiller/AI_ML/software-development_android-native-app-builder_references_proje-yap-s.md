---
name: software-development_android-native-app-builder_references_proje-yap-s
description: Proje Yapısı
title: "Software Development Android Native App Builder References Proje Yap S"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Proje Yapısı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Proje Yapısı
```
<proje_adi>/
├── build.gradle.kts (root — sadece plugin declaration)
├── settings.gradle.kts (repo + include(":app"))
├── gradle.properties (android.useAndroidX=true)
├── local.properties (sdk.dir)
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── gradlew + gradlew.bat
└── app/
    ├── build.gradle.kts (android plugin + dependencies)
    └── src/main/
        ├── AndroidManifest.xml
        ├── java/com/<package>/MainActivity.java
        └── res/
            ├── layout/activity_main.xml
            └── values/
                ├── strings.xml
                └── themes.xml
```
