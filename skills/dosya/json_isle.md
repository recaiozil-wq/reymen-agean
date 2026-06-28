---
title: JSON Dosyası İşleme
description: JSON okuma, yazma, güncelleme, sorgu
tags: [json, veri, python]
---

## JSON oku ve anahtara eriş
PYTHON_CALISTIR "import json; d=json.load(open('data.json')); print(d['anahtar'])"

## JSON yaz
PYTHON_CALISTIR "import json; json.dump({'ad':'test','sayi':42}, open('cikti.json','w'), ensure_ascii=False, indent=2); print('Yazıldı')"

## JSON güncelle
PYTHON_CALISTIR "
import json
with open('data.json') as f: d=json.load(f)
d['yeni_alan'] = 'deger'
with open('data.json','w') as f: json.dump(d, f, ensure_ascii=False, indent=2)
print('Güncellendi')
"
