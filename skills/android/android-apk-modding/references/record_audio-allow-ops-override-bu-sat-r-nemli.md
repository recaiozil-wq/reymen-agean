---
skill_id: d8b62a8df61e
usage_count: 1
last_used: 2026-06-16
---
#        "RECORD_AUDIO: allow" (ops override, bu satır önemli)
```

Bu, uygulamanın arka planda da ses kaydetmesine izin verir. Özellikle "ekran kilitlenince kayıt dursun" sorununu çözebilir.

**İşe yaramazsa:** Uygulamayı kapatıp aç, tekrar dene. Bazı uygulamalar `foreground`→`allow` değişikliğini runtime'da okumaz, restart gerekir.

**2. Bildirim iznini kontrol et:**
```bash
adb shell "appops get com.target.package POST_NOTIFICATION"
```

**3. Uygulamanın debuggable durumunu değiştir (root'suz çalışmaz):**
```bash