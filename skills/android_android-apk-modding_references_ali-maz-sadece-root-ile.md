
> **Kategori:** android

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Android_Android Apk Modding_References_Ali Maz Sadece Root Ile |
| **Nerede?** | android/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# ÇALIŞMAZ — sadece root ile
adb shell "pm set-debug com.target.package true"
```

**4. Uygulama etkinliğini kontrol et:**
```bash
adb shell "dumpsys package com.target.package | grep enabled"