---
name: software-development_android-native-app-builder_references_3-uygulamay-ba-lat
description: 3.
title: "Software Development Android Native App Builder References 3 Uygulamay Ba Lat"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | 3.0 |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# 3. Uygulamayı başlat
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell am start -n com.<package>/.MainActivity

**Pitfall — Git Bash + ADB pull path dönüşümü:** Terminal aracı Git Bash kullanır (`bash`). `adb pull /data/local/tmp/file` gibi bir komut gönderdiğinde Git Bash `/data/local/tmp/file` yolunu `C:/Program Files/Git/data/local/tmp/file` olarak çevirir ve ADB "No such file or directory" hatası alır.
- **Çözüm 1:** Python `execute_code` aracını kullan → `subprocess.run()` ile argümanlar doğrudan geçer, bash araya girmez.
- **Çözüm 2:** `adb.exe shell "cd /data/local/tmp && screencap screen.png"` — shell içinde kal, pull yerine push kullan.
- **Android 16 (API 36) notu:** `screencap` komutu `-p` flag'ini eski sürümler gibi kabul eder ancak sözdizimi `screencap [-ahp] [-d display-id] [FILENAME]` şeklindedir; en kolayı: `screencap /data/local/tmp/screen.png` (çıktı .png uzantısından otomatik tanınır).
