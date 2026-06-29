---
name: software-development_android-native-app-builder_references_pid-den-log
description: PID'den log
title: "Software Development Android Native App Builder References Pid Den Log"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | PID'den log |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# PID'den log
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell logcat -d --pid=<PID>
```

### Servis Durumu Kontrolü
```bash
/c/Users/marko/AppData/Local/Android/Sdk/platform-tools/adb.exe shell dumpsys activity services com.package
