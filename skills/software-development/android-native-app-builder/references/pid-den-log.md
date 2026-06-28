---
skill_id: e2b1948a0f64
usage_count: 1
last_used: 2026-06-16
---
# PID'den log
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell logcat -d --pid=<PID>
```

### Servis Durumu Kontrolü
```bash
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell dumpsys activity services com.package