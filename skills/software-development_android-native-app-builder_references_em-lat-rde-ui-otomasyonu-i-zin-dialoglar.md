---
name: software-development_android-native-app-builder_references_em-lat-rde-ui-otomasyonu-i-zin-dialoglar
description: Emülatörde UI Otomasyonu (İzin Dialogları)
title: "Software Development Android Native App Builder References Em Lat Rde Ui Otomasyonu I Zin Dialoglar"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Emülatörde UI Otomasyonu (İzin Dialogları) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

## Emülatörde UI Otomasyonu (İzin Dialogları)

Emülatörde uygulama test ederken Android izin dialogları (mikrofon, bildirim, depolama) manuel müdahale gerektirir. **uiautomator + ADB ile programatik çözüm:**

### 1. UI Dump Al
```bash
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell uiautomator dump /sdcard/ui.xml
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe pull /sdcard/ui.xml /c/Users/marko/Desktop/
```

### 2. Buton Koordinatlarını Bul (Python/regex)
```python
import re
with open('ui.xml', 'r') as f:
    content = f.read()
for text, bounds in re.findall(r'text="([^"]*)"[^>]*bounds="([^"]*)"', content):
    if text.strip():
        print(f"'{text}' -> {bounds}")
