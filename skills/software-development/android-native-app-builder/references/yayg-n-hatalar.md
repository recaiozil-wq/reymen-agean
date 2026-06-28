---
skill_id: 668ef8b5cacf
usage_count: 1
last_used: 2026-06-16
---
## Yaygın Hatalar
| Hata | Çözüm |
|------|-------|
| `dependencyResolution` hatası | `dependencyResolutionManagement` olarak düzelt |
| `android.useAndroidX` | `gradle.properties`'e ekle |
| SDK license kabulü | `yes | sdkmanager --licenses` |
| build-tools versiyonu | Gradle otomatik eksik olanı indirir |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | İmza uyuşmazlığı — önce `adb uninstall com.package` yap, sonra tekrar `adb install` |
| `INSTALL_FAILED_ALREADY_EXISTS` | `adb install -r` ile yeniden dene (replace) |