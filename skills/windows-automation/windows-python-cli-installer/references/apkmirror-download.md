---
skill_id: 43dba7db1514
usage_count: 1
last_used: 2026-06-16
---
# APKMirror'dan APK İndirme (Python ile)

APKMirror, APK dosyalarını doğrudan `curl` ile indirmeye izin vermez. Sayfa yönlendirme/referrer kontrolü yapar.

## Yöntem

APKMirror sayfasından JavaScript ile indirme linkini bul:

```javascript
// Browser console'dan
document.querySelector('a[href*="download.php"]')?.href
```

## Python ile İndirme

```python
import urllib.request

url = "https://www.apkmirror.com/wp-content/themes/APKMirror/download.php?id=XXXXX&key=YYYYY"
output = r"C:\Users\marko\re-hermes\file.apk"

req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.apkmirror.com/...release/",
    "Accept": "*/*"
})

with urllib.request.urlopen(req, timeout=60) as resp:
    data = resp.read()
    with open(output, "wb") as f:
        f.write(data)
```

## Önemli Noktalar

- **Referer header'ı ZORUNLU** — APKMirror download.php referrer kontrolü yapar
- **User-Agent** da gerekli (bot engellemesi)
- `content-type: application/vnd.apkm` → APK bundle (split APK)
- `curl -L` ile direkt indirme çalışmaz (referrer eksik)

## APK Analiz

APK'ler RE-ReYMeN ile analiz edilebilir:
```bash
re-hermes dosya.apk
```

Not: APK'ler ZIP sıkıştırması kullandığı için entropy her zaman yüksektir (7.5+). Bu AI yorumunda false positive üretebilir.
