---
name: user-preferences_3lu-kontrol-sistemi_references_log-kayit-formati
description: Günlük Kayıt Format Şablonu
title: "User Preferences 3Lu Kontrol Sistemi References Log Kayit Formati"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Günlük Kayıt Format Şablonu |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Günlük Kayıt Format Şablonu

## Dosya Yolu
```
C:\Users\marko\OneDrive\Desktop\hermes calisma gunlugu\hermes GG.AA.YYYY.txt
```

## Başlık Formatı
```
HERMES ÇALIŞMA GÜNLÜĞÜ — GG.AA.YYYY
====================================
```

## Madde Formatı
```
N. MADDE ADI
   - Kullanıcı: "kullanıcının aynen yazılmış sözü"
   - Yapılan işlem: komut/adım açıklaması
   - Not/varsa hata: ek bilgi
```

## Örnek
```
HERMES ÇALIŞMA GÜNLÜĞÜ — 12.06.2026
====================================

1. DOSYA OLUŞTURMA
   - Kullanıcı: "masa ustunde baba bos bir dosya olustur"
   - touch ile oluşturuldu
   - Hata: Uzantısız dosya oluşturuldu, Windows açamadı
   - Alınan ders: tüm dosyalara .txt uzantısı eklenecek
```

## Kurallar
- Her işlem anında yazılır, biriktirilmez
- Kullanıcının söylediği cümle aynen yazılır, düzeltilmez
- Her işlem ayrı numaralı madde
- Başarısız işlem de kaydedilir (hata + çözüm)
- Günlük kullanıcı tarafından denetlenir
