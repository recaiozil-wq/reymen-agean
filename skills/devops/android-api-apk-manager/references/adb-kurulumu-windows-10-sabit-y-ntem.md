---
skill_id: 7146eb37bbfc
usage_count: 1
last_used: 2026-06-16
---
## ADB Kurulumu (Windows 10 — sabit yöntem)
PATH’te `adb` yoksa şu adımları otomatik uygula:
1. İndir: `curl -o /tmp/platform-tools-latest-windows.zip https://dl.google.com/android/repository/platform-tools-latest-windows.zip`
2. Çıkar: `unzip -q /tmp/platform-tools-latest-windows.zip -d "$LOCALAPPDATA/Android/Sdk/"`
3. PATH’e ekle: `setx PATH "$PATH;$LOCALAPPDATA\Android\Sdk\platform-tools"` (Windows kalıcı PATH)
4. Doğrula: `adb version`

*Not: Windows'ta "Path boşluğu/özel karakter" hatası alırsan komutları tırnakla sar (ör. `python 'C:\...\android_scan.py'`).*