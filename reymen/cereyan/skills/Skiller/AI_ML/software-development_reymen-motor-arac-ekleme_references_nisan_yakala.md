---
name: software-development_reymen-motor-arac-ekleme_references_nisan_yakala
description: nisan_yakala.py — Gorsel Sablon Yakalama Araci
title: "Software Development Reymen Motor Arac Ekleme References Nisan Yakala"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | nisan_yakala.py — Gorsel Sablon Yakalama Araci |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# nisan_yakala.py — Gorsel Sablon Yakalama Araci

**Dosya:** `C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\nisan_yakala.py`
**Boyut:** 96 satir, ~3 KB

## Amac
OpenCV template matching icin kullanilacak .png sablonlarini canli ekrandan yakalar.

## Kullanim
```bash
python nisan_yakala.py
# Fareyi hedef buton/alan uzerine getir -> ENTER
# 2sn onizleme -> isim gir ("giris_buton") -> .ReYMeN/nisanlar/ kaydedilir
# ESC ile cikis
```

## Teknik Detay
- `mss.mss()` ile tam ekran yakala
- `ctypes.windll.user32.GetCursorPos()` ile fare konumu
- Fare etrafinda 80x80 px kirp (40px offset)
- `cv2.imshow()` ile 2sn onizleme
- `cv2.imwrite()` ile `.ReYMeN/nisanlar/{ad}.png` kaydet

## Cikarilmasi Onerilen Sablonlar
| Dosya | Hedef |
|-------|-------|
| `giris_buton.png` | Login sayfasindaki giris butonu |
| `kayit_buton.png` | Kaydol butonu |
| `captcha_kutu.png` | CAPTCHA / guvenlik kutusu |
| `onay_kutusu.png` | Onay checkbox'i |
| `siparis_buton.png` | Satın Al butonu |
| `ad_alani.png` | Ad input alani |
| `soyad_alani.png` | Soyad input alani |
| `eposta_alani.png` | E-posta input alani |
| `sifre_alani.png` | Sifre input alani |
| `telefon_alani.png` | Telefon input alani |

## Onemli
- Sablonlar Tor Browser'in **letterboxing** cozunurlugu ile ayni boyutta alinmali
- Guven esigi: `NisanBulucu` icin varsayilan %75
- 80x80 px standart boyut, farkli boyutlarda OpenCV eslesme basarisi duser
