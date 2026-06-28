---
title: Metin İşleme ve Regex
description: String işlemleri, regex, metin temizleme, parse etme
tags: [metin, regex, string, parse, temizleme]
---

## Regex ile veri çıkar
PYTHON_CALISTIR "
import re
metin = 'E-posta: ali@example.com, Tel: +90-555-1234567'
email = re.findall(r'[\w.+-]+@[\w-]+\.[a-z]{2,}', metin)
tel   = re.findall(r'\+\d[\d\-\s]{8,}', metin)
print(f'Email: {email}')
print(f'Tel: {tel}')
"

## Metin temizleme
PYTHON_CALISTIR "
import re
metin = '  Fazla   boşluklar  ve\n\nSatır sonu   '
temiz = re.sub(r'\s+', ' ', metin).strip()
print(repr(temiz))
"

## Markdown'dan düz metin
PYTHON_CALISTIR "
import re
md = '# Başlık\n**kalın** ve *italik* [link](http://site.com)'
duz = re.sub(r'[*_#\[\]()]|http\S+', '', md).strip()
print(duz)
"

## CSV satırı parse et
PYTHON_CALISTIR "
import csv, io
satir = '\"ad soyad\",42,\"istanbul, türkiye\"'
parsed = list(csv.reader(io.StringIO(satir)))[0]
print(parsed)
"
