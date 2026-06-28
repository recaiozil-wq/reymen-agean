---
skill_id: 6d462a8bd542
usage_count: 1
last_used: 2026-06-16
---
# Seçenek B — apksigner (V2+V3 garanti, tercih edilen)
apksigner sign --ks my.keystore --ks-key-alias myalias --v1-signing-enabled true --v2-signing-enabled true --v3-signing-enabled true --out signed.apk rebuilt_unsigned.apk
apksigner verify --verbose signed.apk
```

**apksigner yolu:** Android SDK build-tools içinde:
```bash
"/c/Users/marko/AppData/Local/Android/Sdk/build-tools/35.0.0/apksigner" sign --ks my.keystore --ks-key-alias myalias rebuilt_unsigned.apk
```

#### 7. Split APK'ları Birleştir (varsa)

apktool bazen `base.apk` + `split_config.arm64_v8a.apk` olarak iki dosya üretir. Single APK gerekiyorsa:

```bash