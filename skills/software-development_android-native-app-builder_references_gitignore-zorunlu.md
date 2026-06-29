---
name: software-development_android-native-app-builder_references_gitignore-zorunlu
description: .gitignore (Zorunlu)
title: "Software Development Android Native App Builder References Gitignore Zorunlu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | .gitignore (Zorunlu) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## .gitignore (Zorunlu)

Android projelerinde `.gitignore` kök dizinde olmalı. **`/build` değil, `**/build` kullan** — çünkü `app/build/` alt klasörü de var:

```gitignore
*.iml
.gradle
**/build
/captures
.externalNativeBuild
.cxx
local.properties
release.keystore
nul
.idea/
.DS_Store
*.apk
*.aab
*.keystore
*.jks
```

### Pitfall: `nul` dosyası (Windows)

Windows'ta Gradle bazen `nul` adında 0-byte'lık garip bir dosya oluşturur. Git bunu index'leyemez (`error: short read while indexing nul`). **Çözüm:**

```bash
