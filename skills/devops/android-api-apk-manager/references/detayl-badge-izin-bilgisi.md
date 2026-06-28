---
skill_id: 720631f13a52
usage_count: 1
last_used: 2026-06-16
---
# Detaylı badge/izin bilgisi
"/c/Users/marko/AppData/Local/Android/Sdk/build-tools/34.0.0/aapt" dump badging "<apk_yolu>"
```

**Çıktıda kontrol edilecekler:**
| Alan | Ne aranır |
|------|-----------|
| `package:` | Paket adı (örn. `com.livetranscriber`) |
| `targetSdkVersion:` | Telefonun Android sürümüne uygun mu? |
| `sdkVersion:` | Minimum SDK (eski cihazlar için 26+ yeterli) |
| `uses-permission:` | İzinler (RECORD_AUDIO, INTERNET, vb.) |
| `launchable-activity:` | Ana Activity adı |
| `application-label:` | Uygulama görünen adı |