---
skill_id: 9afd2c0b4c72
usage_count: 1
last_used: 2026-06-16
---
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