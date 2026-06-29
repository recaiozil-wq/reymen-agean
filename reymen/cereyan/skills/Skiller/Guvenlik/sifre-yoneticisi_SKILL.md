--- 
title: Şifre Yöneticisi
name: sifre-yoneticisi
description: Güvenli şifre oluşturma, şifre gücü analizi ve hassas bilgi yönetimi
tags: [guvenlik, sifre, hash, sifreleme, guvenli-saklama]
---

# Şifre Yöneticisi

| 5N1K | Açıklama |
|------|----------|
| Kim | ReYMeN bot kullanıcıları |
| Ne | Güçlü şifreler oluşturur, mevcut şifrelerin gücünü analiz eder ve hassas bilgileri yönetir |
| Nerede | reymen/cereyan/skills/Skiller/Guvenlik/ |
| Ne Zaman | Yeni hesap oluşturma, şifre değiştirme veya güvenlik denetimi gerektiğinde |
| Neden | Zayıf/tekrar eden şifreler en büyük güvenlik açığıdır; bot güçlü şifreler üretebilir |
| Nasıl | secrets modülü ile rastgele şifre üretimi, zxcvbn ile güç analizi yapılır |

## Şifre Oluşturma

| Mod | Uzunluk | Karakter Seti | Örnek |
|-----|---------|---------------|-------|
| Basit | 12 | a-z, A-Z, 0-9 | `Kd8mR3xP9qL2` |
| Güçlü | 20 | + özel karakterler | `Kd8m!R3xP9qL2#vY5nW` |
| Parola | 4 kelime | Sözlük tabanlı | `mavi-aydinlik-robot-42` |
| PIN | 6 | 0-9 | `847291` |

## Şifre Gücü Analizi

| Puan | Seviye | Anlamı |
|------|--------|--------|
| 0-20 | Çok zayıf | 1sn'de kırılır |
| 20-40 | Zayıf | Sözlük saldırısıyla kırılır |
| 40-60 | Orta | Brute-force ile kırılabilir |
| 60-80 | Güçlü | Yıllar sürebilir |
| 80-100 | Çok güçlü | Pratikte kırılamaz |

## Güvenli Saklama

- Şifreler asla düz metin olarak hafızaya kaydedilmez
- `hashlib.sha256` ile hash'lenerek saklanır
- Hassas bilgiler için OS keyring veya env değişkenleri kullanılır
