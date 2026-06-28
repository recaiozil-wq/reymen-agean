---
name: software-development_android-native-app-builder_references_bounds-left-top-right-bottom-center-left-right-2-top-bottom-
description: bounds="[left,top][right,bottom]" → center = ((left+right)/2, (top+bottom)/2)
title: "Software Development Android Native App Builder References Bounds Left Top Right Bottom Center Left Right 2 Top Bottom "
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | bounds="[left,top][right,bottom]" → center = ((left+right)/2, (top+bottom)/2) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# bounds="[left,top][right,bottom]" → center = ((left+right)/2, (top+bottom)/2)
```

### 3. Tıkla
```bash
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell input tap <center_x> <center_y>
```

### İzin Sırası (LiveTranscriber örneği)
İzin dialogları **sırayla** gelir. Birini yanıtlamadan diğeri görünmez:
1. **RECORD_AUDIO** → "While using the app" (center 720,1590)
2. **POST_NOTIFICATIONS** (Android 13+) → "Allow" (center 720,1695)
   - Foreground Service çalıştırmak için bildirim izni zorunlu

**Pitfall:** BAŞLAT butonuna basınca önce MİKROFON izni gelir, sonra BİLDİRİM izni gelir. İkinci izin gelene kadar `uiautomator dump` ile UI'yi tekrar kontrol et. Arada `sleep 3-5` bırak.

**Kısayol — ADB ile tüm izinleri tek seferde ver (UI tıklamaya gerek kalmaz):**
```bash
adb shell pm grant com.package android.permission.RECORD_AUDIO
adb shell pm grant com.package android.permission.POST_NOTIFICATIONS
