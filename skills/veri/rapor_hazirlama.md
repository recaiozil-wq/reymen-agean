---
title: Rapor Hazırlama
description: Veri toplama, özetleme ve markdown rapor oluşturma
tags: [rapor, markdown, ozet, dokumantasyon]
---

## Markdown rapor oluştur
PYTHON_CALISTIR "
from datetime import datetime
rapor = f'''# Rapor — {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Özet
- Toplam: 42
- Başarılı: 38
- Başarısız: 4

## Detaylar
| Alan | Değer |
|------|-------|
| CPU  | %23   |
| RAM  | 8.2GB |

## Sonuç
Sistem normal çalışıyor.
'''
with open('rapor.md', 'w', encoding='utf-8') as f:
    f.write(rapor)
print('Rapor yazıldı: rapor.md')
"

## JSON'dan HTML tablo
PYTHON_CALISTIR "
veri = [{'ad': 'Ali', 'puan': 95}, {'ad': 'Veli', 'puan': 87}]
satir = ''.join(f'<tr><td>{d[\"ad\"]}</td><td>{d[\"puan\"]}</td></tr>' for d in veri)
html = f'<table><tr><th>Ad</th><th>Puan</th></tr>{satir}</table>'
print(html)
"
