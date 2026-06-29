---
name: software-development_hermes-vs-claude-kod-kalitesi_references_xray-protokolu
description: XRAY Kod Analiz Protokolu
title: "Software Development Hermes Vs Claude Kod Kalitesi References Xray Protokolu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | XRAY Kod Analiz Protokolu |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

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
