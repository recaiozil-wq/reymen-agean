---
skill_id: f5c0fd22ca34
usage_count: 1
last_used: 2026-06-16
---
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