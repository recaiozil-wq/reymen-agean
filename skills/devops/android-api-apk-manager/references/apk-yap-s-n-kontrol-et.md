---
skill_id: c2dd7f03185d
usage_count: 1
last_used: 2026-06-16
---
# APK yapısını kontrol et
aapt2 dump badging "orijinal.apk" | grep -E "package:|minSdkVersion:|targetSdkVersion:|native-code:|split:"