---
name: software-development_hermes-vs-claude-kod-kalitesi_references_xray-kod-analizi
description: XRAY Kod Analizi Teknigi
title: "Software Development Hermes Vs Claude Kod Kalitesi References Xray Kod Analizi"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | XRAY Kod Analizi Teknigi |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# XRAY Kod Analizi Teknigi

Kullanici yuzeysel grep analizini kabul etmez. 'XRAY' derinlemesine inceleme ister.
Bir kere bakip gecmek yetmez — periyodik olarak takip et.

## XRAY Protokolu

1. **Dosya yapisi**: satir sayisi, class/fonksiyon sayisi, try/except sayisi
2. **Import zinciri**: hangi modul hangisini import ediyor, gercek calisma testi
3. **Mantiksal akis semasi**: main() -> sinif -> metod -> alt metod akisi
4. **Calisma testi**: `python -c "from X import Y"` ile her modulu import et
5. **Derleme**: `python -m py_compile` ile tum dosyalar (unix shell uzerinden)
6. **Kritik bulgu**: import edilmis ama kullanilmamis, hata yakalanmamis, eksik parametre
7. **Surekli izleme**: `find . -name "*.py" -mmin -3` ile 3 dakikada bir kontrol et

## Satir Satir Dogrulama (Line-by-Line Review)

Bu kullanici kodu satir satir kontrol eder. Asla "calisiyor" diye gecme.
Her satiri ayri ayri goster ve onay al.

Protokol:
1. `head` veya `sed -n` ile belirli satirlari goster
2. Her import, her degisken, her fonksiyon imzasi ayri ayri dogrulanir
3. Kullanici bir satiri soyler -> sen o satiri gosterirsin -> kullanici onaylar
4. Onay almadigin hicbir satiri "bitti" sayma
5. Kullanici "(empty)" yazarsa bir sonraki bolume gec

Kullanici su siralamayi takip eder:
encoding -> docstring -> imports -> sabitler -> class tanimi -> __init__ -> her metod -> fonksiyonlar -> CLI -> if __name__

## Agent Karsilastirma Metodolojisi

Iki AI ajaninin kodunu karsilastirirken:

1. **Metrik topla**: satir sayisi, class/fonk sayisi, try/except sayisi, docstring sayisi
2. **Import zincirini karsilastir**: ayni isi yapan moduller var mi?
3. **Calisma testi yap**: her iki kod da calisiyor mu?
4. **Yaklasim farki**: butunsel mi (ozellik+CLI+hata+dokumantasyon) yoksa odakli patch mi?
5. **Ders cikar**: hangi pattern'ler kullanilmis, hangileri atlanmis?

## Araclar

- `find . -name "*.py" -mmin -3` — son 3 dakikada degisen dosyalar
- `python -m py_compile dosya.py` — derleme kontrolu
- `python -c "from modul import sinif"` — import testi
- `grep -n "class\|def " dosya.py` — yapi analizi
- `wc -l dosya.py` — satir sayisi
- `find . -path "*__pycache__*" -delete` — pycache temizle (import sorunlarinda)
- `sed -n 'N,Mp' dosya.py` — belirli satir araligini goster (satir satir dogrulama icin)
