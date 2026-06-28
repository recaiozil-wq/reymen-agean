---
title: Python ile Dosya İşleme
description: Python kodu çalıştırarak dosya kopyalama, taşıma, yeniden adlandırma
tags: [python, dosya, shutil, glob]
---

## Dosya Kopyalama
PYTHON_CALISTIR "import shutil; shutil.copy('kaynak.txt', 'hedef.txt'); print('Kopyalandı')"

## Tüm .txt dosyalarını listele
PYTHON_CALISTIR "import glob; print('\n'.join(glob.glob('**/*.txt', recursive=True)))"

## Dosya büyüklüğü kontrol
PYTHON_CALISTIR "import os; print(f'{os.path.getsize(\"dosya.txt\"):,} byte')"

## Dizin oluştur
PYTHON_CALISTIR "from pathlib import Path; Path('yeni_klasor/alt').mkdir(parents=True, exist_ok=True); print('Oluşturuldu')"
