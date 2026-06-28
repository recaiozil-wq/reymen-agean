---
skill_id: 99cd41dbc50b
usage_count: 1
last_used: 2026-06-16
---
## Convention Plugins (Gradle)

For KMP projects, use convention plugins to reduce build file duplication:

```kotlin
// build-logic/src/main/kotlin/kmp-library.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
}

kotlin {
    androidTarget()
    iosX64(); iosArm64(); iosSimulatorArm64()
    sourceSets {
        commonMain.dependencies { /* shared deps */ }
        commonTest.dependencies { implementation(kotlin("test")) }
    }
}
```

Apply in modules:

```kotlin
// domain/build.gradle.kts
plugins { id("kmp-library") }
```