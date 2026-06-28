---
skill_id: ed9701c58125
usage_count: 1
last_used: 2026-06-16
---
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
