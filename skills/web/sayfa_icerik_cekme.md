---
title: Web Sayfası İçerik Çekme
description: URL'den metin içeriği çekme, temizleme, özetleme
tags: [web, scraping, icerik, urllib, playwright]
---

## Sayfa içeriği al
WEB_ICERIK "https://example.com"

## Birden fazla sayfadan içerik topla
PYTHON_CALISTIR "
import urllib.request
urls = ['https://site1.com', 'https://site2.com']
for url in urls:
    with urllib.request.urlopen(url, timeout=10) as r:
        print(r.read().decode('utf-8', errors='replace')[:500])
"

## JavaScript gerektiren sayfalar için
BROWSER_HEADLESS "https://spa-app.com"

## PDF indirme
PYTHON_CALISTIR "
import urllib.request
urllib.request.urlretrieve('https://example.com/belge.pdf', 'belge.pdf')
print('PDF indirildi')
"

---
## Yeni Varyasyonlar / Ek Adimlar (2026-06-16 15:26)

1. requests ile sayfayi indir
2. BeautifulSoup ile parse et

---
## Yeni Varyasyonlar / Ek Adimlar (2026-06-16 15:26)

3. Selenium ile JS render bekle
4. Dinamik icerigi yakala
