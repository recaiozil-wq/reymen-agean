---
skill_id: 222ad9d98b22
usage_count: 1
last_used: 2026-06-16
---
# APK'yı doküman olarak gönder
with open(apk_path, 'rb') as f:
    files = {'document': ('UygulamaAdi.apk', f, 'application/vnd.android.package-archive')}
    data = {'chat_id': chat_id, 'caption': 'APK açıklaması'}
    resp = requests.post(f'https://api.telegram.org/bot{token}/sendDocument', files=files, data=data, timeout=30)

print(f"Status: {resp.status_code}")
```

**Önemli:** Chat ID = `TELEGRAM_HOME_CHANNEL` (.env'de). Bu ID genellikle `6328823909` formatındadır. Dosyayı `/c/Users/marko/Desktop/` altına da kopyala ki bilgisayarda da bulunsun.