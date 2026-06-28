---
title: Sistem Komutu Çalıştırma
description: Windows komutları, powershell, subprocess kullanımı
tags: [sistem, komut, windows, powershell, subprocess]
---

## Temel komut çalıştırma
KOMUT_CALISTIR "dir C:\Users\kullanici\Desktop"

## PowerShell komutu
KOMUT_CALISTIR "powershell -Command \"Get-Process | Sort CPU -Desc | Select -First 10\""

## Çıktıyı yakala
PYTHON_CALISTIR "
import subprocess
sonuc = subprocess.run(['dir'], shell=True, capture_output=True, text=True)
print(sonuc.stdout[:500])
"

## Arka planda çalıştır
PYTHON_CALISTIR "
import subprocess
p = subprocess.Popen(['python', 'script.py'], stdout=subprocess.PIPE)
print(f'PID: {p.pid}')
"

## Sistem bilgisi
KOMUT_CALISTIR "systeminfo | findstr /B /C:\"OS Name\" /C:\"Total Physical Memory\""
