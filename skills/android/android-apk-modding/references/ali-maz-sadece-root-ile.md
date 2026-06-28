---
skill_id: 50f034b23497
usage_count: 1
last_used: 2026-06-16
---
# ÇALIŞMAZ — sadece root ile
adb shell "pm set-debug com.target.package true"
```

**4. Uygulama etkinliğini kontrol et:**
```bash
adb shell "dumpsys package com.target.package | grep enabled"