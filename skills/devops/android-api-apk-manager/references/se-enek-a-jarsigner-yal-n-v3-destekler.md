---
skill_id: d17cfa602a1d
usage_count: 1
last_used: 2026-06-16
---
# Seçenek A — jarsigner (yalın, V3 destekler)
keytool -genkey -v -keystore my.keystore -alias myalias -keyalg RSA -keysize 2048 -validity 10000
jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 -keystore my.keystore rebuilt_unsigned.apk myalias
jarsigner -verify -verbose rebuilt_unsigned.apk