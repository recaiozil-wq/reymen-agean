---
skill_id: b9f0e7aec87a
usage_count: 1
last_used: 2026-06-16
---
## APK Modding (Decompile → Modify → Rebuild → Sign)

Varolan bir APK'yı tersine mühendislik ile değiştirmek için bu workflow'u izle.

### Gereksinimler
- `apktool.jar` (en son sürüm, indir: `https://github.com/iBotPeaches/Apktool/releases`)
- `uber-apk-signer.jar` (isteğe bağlı, imza için)
- `jarsigner` veya `apksigner` (JDK ile gelir)
- Java JDK 17+
- `aapt2` (Android SDK build-tools içinde)

### Adımlar

#### 1. APK İndir
```bash