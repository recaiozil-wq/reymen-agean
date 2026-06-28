---
skill_id: e7559da61d8c
usage_count: 1
last_used: 2026-06-16
---
# XRAY Kod Analiz Protokolu

Kod tabanini derinlemesine analiz ederken su adimlar izlenir:

## Adim 1: Dosya Yapisi
- Kac dosya var? (.py, .bat, .env)
- Klasor yapisi nedir?
- En buyuk dosyalar hangileri? (boyut/satir)

## Adim 2: Derleme
- `python -m py_compile *.py` — tum dosyalar derleniyor mu?
- `ast.parse()` ile syntax kontrolu

## Adim 3: Import Zinciri
- Her modul birbirini import edebiliyor mu?
- Circular import var mi?
- Conditional import (try/except) dogru kullanilmis mi?

## Adim 4: Runtime Test
- Kritik siniflari import et
- Basit bir instance olustur
- Metodlardan birini cagir

## Adim 5: Env Kontrolu
- `.env` dosyasi temiz mi? (bos satir, yorum karismasi var mi?)
- `***` prefixli degerler dogru kontrol ediliyor mu? (`startswith("***")` ile, `== "***"` DEGIL)

## Adim 6: Kalite
- Her fonksiyonda docstring var mi?
- try/except var mi?
- argparse/CLI --help destegi var mi?
