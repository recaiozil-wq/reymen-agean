---
title: Python Hata Ayıklama
description: Python kod hatalarını tespit etme, traceback okuma, düzeltme
tags: [python, debug, hata, traceback]
---

## Hata türünü tanı
- ImportError → modül kurulu değil, pip install yap
- FileNotFoundError → dosya yolu yanlış, DIZIN_LISTELE ile kontrol et
- AttributeError → nesne metodunu kontrol et, dir() kullan
- TypeError → tip uyuşmazlığı, type() ile kontrol et

## Adım adım hata ayıklama
PYTHON_CALISTIR "
try:
    # sorunlu kod buraya
    pass
except Exception as e:
    import traceback
    print(traceback.format_exc())
"

## Modül var mı kontrol
PYTHON_CALISTIR "import importlib; spec = importlib.util.find_spec('modul_adi'); print('VAR' if spec else 'YOK')"

## Değişken değerini izle
PYTHON_CALISTIR "x = hesapla(); print(f'x={x!r}, tip={type(x).__name__}')"
