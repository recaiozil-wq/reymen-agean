---
skill_id: b08ddaacb9b3
usage_count: 1
last_used: 2026-06-16
---
## Troubleshooting — Sessiz Hataların Kök Sebebi

| Hata | Gerçek Sebep | Çözüm |
|------|-------------|-------|
| "Parse error" / "Package invalid" | .so dosyaları DEFLATE ile sıkıştırılmış | ZIP_STORED ile yeniden paketle |
| Installation "incompatible" | isSplitRequired kaldırılmamış | Manifest'ten split referanslarını sil |
| App opens then crashes silently | Resource ID yanlış | public.xml'den ID'yi teyit et |
| "App not installed" / INSTALL_FAILED_UPDATE_INCOMPATIBLE | İmza çakışması (farklı keystore) veya sistem uygulaması | Eski sürümü kaldır (`adb uninstall --user 0`). Sistem uygulamasıysa + reboot dene. Hala olmazsa → root gerekir. Kullanıcıya bildir. |
| INSTALL_FAILED_MISSING_SPLIT | Split APK base'den ayrı yükleniyor | Manifest'ten `requiredSplitTypes` + `splitTypes` taglerini sil. Meta-data'dan `splits.required`, `com.android.vending.splits` kaldır. |
| Google Play Services broken | Orijinal imza gitti — GMSCore reddediyor | Kaçınılmaz. Alternatif API stratejisi |
| apktool b hata vermiyor ama APK yok | Java heap yetersiz | `export JAVA_OPTS="-Xmx4g"` ile tekrar dene |
| `pm install` sdcard'dan "Can't open file" | system_server sdcard'a erişemez | APK'yı `/data/local/tmp/`'e push et, ordan kur: `adb push apk /data/local/tmp/` + `adb shell pm install -r -t /data/local/tmp/apk` |
| `appops set` çalışıyor ama uygulama hala foreground davranıyor | Uygulama runtime'da ops değişikliğini okumaz, restart gerekir | Uygulamayı kapatıp aç: `adb shell am force-stop com.package` + manuel başlat |
| Auto Blocker / Play Protect engelliyor | Samsung Auto Blocker veya Google Play Protect | ADB ile kapat: `adb shell settings put global package_verifier_enable 0 && adb shell settings put global verifier_verify_adb_installs 0 && adb shell settings put global auto_blocker_enabled 0 && adb shell settings put secure auto_blocker_enabled 0`. Veya direkt `adb install` dene (Auto Blocker'ı bypass eder). |
| Sistem uygulamasına yama yapılamıyor (Android 16+, One UI 8) | `INSTALL_FAILED_UPDATE_INCOMPATIBLE` — reboot sonrası bile düzelmez | **Package rename stratejisi dene** (references/package-rename-bypass.md). Root'suz tek çözüm: rename + sideload. |
| `INSTALL_FAILED_DUPLICATE_PERMISSION` | `<permission>` ismi eski pakette kalmış | Manifest'teki permission string'ini yeni paket adına çevir |
| `INSTALL_FAILED_CONFLICTING_PROVIDER` | `<provider android:authorities>` çakışıyor | Provider authority'yi yeni paket adına çevir |
| `ClassNotFoundException` (package rename sonrası) | Smali'de class reference veya layout'ta custom view değişmemiş | Tüm smali + res XML'lerde eski paket adını tara ve değiştir |