---
title: Ortam Değişkenleri ve .env
description: .env dosyası okuma, API key yönetimi, güvenli config
tags: [env, config, api_key, guvenlik, dotenv]
---

## .env oku
PYTHON_CALISTIR "
from dotenv import load_dotenv
import os
load_dotenv('.env')
api_key = os.environ.get('OPENAI_API_KEY', '')
print('Key var mı:', bool(api_key and not api_key.startswith('***')))
"

## .env'e yeni değer ekle
PYTHON_CALISTIR "
from pathlib import Path
env = Path('.env')
satir = 'YENI_ANAHTAR=deger\n'
if 'YENI_ANAHTAR' not in env.read_text():
    env.write_text(env.read_text() + satir)
    print('Eklendi')
else:
    print('Zaten var')
"

## Tüm ayarları listele (değerleri gizle)
PYTHON_CALISTIR "
from pathlib import Path
for satir in Path('.env').read_text().splitlines():
    if '=' in satir and not satir.startswith('#'):
        ad, _ = satir.split('=', 1)
        print(f'{ad}=[GİZLİ]')
"

## setup_keys.py ile interaktif kurulum
KOMUT_CALISTIR "python setup_keys.py --liste"
