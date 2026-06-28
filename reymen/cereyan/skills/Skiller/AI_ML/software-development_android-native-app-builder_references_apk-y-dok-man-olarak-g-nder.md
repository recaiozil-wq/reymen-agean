---
name: software-development_android-native-app-builder_references_apk-y-dok-man-olarak-g-nder
description: APK'yı doküman olarak gönder
title: "Software Development Android Native App Builder References Apk Y Dok Man Olarak G Nder"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | APK'yı doküman olarak gönder |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# APK'yı doküman olarak gönder
with open(apk_path, 'rb') as f:
    files = {'document': ('UygulamaAdi.apk', f, 'application/vnd.android.package-archive')}
    data = {'chat_id': chat_id, 'caption': 'APK açıklaması'}
    resp = requests.post(f'https://api.telegram.org/bot{token}/sendDocument', files=files, data=data, timeout=30)

print(f"Status: {resp.status_code}")
```

**Önemli:** Chat ID = `TELEGRAM_HOME_CHANNEL` (.env'de). Bu ID genellikle `6328823909` formatındadır. Dosyayı `/c/Users/marko/Desktop/` altına da kopyala ki bilgisayarda da bulunsun.
