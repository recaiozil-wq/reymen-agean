---
title: Dosya Okuma ve Yazma
description: Yerel dosyaları okuma, yazma, ekleme ve silme işlemleri
tags: [dosya, okuma, yazma, metin]
---

## Dosya Okuma
DOSYA_OKU "dosya_yolu.txt"

## Dosya Yazma (üzerine yaz)
DOSYA_YAZ "hedef.txt" "içerik buraya"

## Dizin Listeleme
DIZIN_LISTELE "C:/Users/kullanici/Belgeler"

## Büyük dosyaları parça parça oku
- Önce DOSYA_OKU ile ilk 100 satırı al
- Gerekirse PYTHON_CALISTIR ile tail/head mantığı uygula
