---
title: Proses Yönetimi
description: Çalışan süreçleri listele, kapat, izle
tags: [proses, psutil, taskkill, sistem]
---

## Çalışan prosesleri listele
PYTHON_CALISTIR "
import psutil
for p in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    if p.info['cpu_percent'] > 1:
        print(f\"{p.info['pid']:6d} {p.info['name']:30s} CPU:{p.info['cpu_percent']:.1f}%\")
"

## Belirli prosesi bul
PYTHON_CALISTIR "
import psutil
hedef = 'python'
bulundu = [p for p in psutil.process_iter(['pid','name']) if hedef.lower() in p.info['name'].lower()]
for p in bulundu:
    print(f\"PID:{p.info['pid']} {p.info['name']}\")
"

## Proses kapat (Windows)
KOMUT_CALISTIR "taskkill /F /IM hedef.exe"

## RAM kullanımı
PYTHON_CALISTIR "
import psutil
ram = psutil.virtual_memory()
print(f'Toplam: {ram.total/1e9:.1f}GB')
print(f'Kullanılan: {ram.used/1e9:.1f}GB ({ram.percent}%)')
print(f'Boş: {ram.available/1e9:.1f}GB')
"
