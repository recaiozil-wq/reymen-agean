---
name: software-development_reymen-motor-arac-ekleme_references_tor_otomasyonu
description: tor_otomasyonu.py — Referans
title: "Software Development Reymen Motor Arac Ekleme References Tor Otomasyonu"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | tor_otomasyonu.py — Referans |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# tor_otomasyonu.py — Referans

**Dosya:** `C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\tor_otomasyonu.py`
**Boyut:** ~480 satir, ~19 KB

## Bilesenler

### TorBrowserKontrol
- Windows'ta Tor Browser'i standart konumlarda arar (`C:\Users\...\Desktop\Tor Browser\Browser\firefox.exe`)
- Selenium `FirefoxOptions` ile SOCKS proxy (127.0.0.1:9150) ayarlar
- `geckodriver` ile WebDriver baglantisi
- Sayfa yukleme timeout: 45sn (Tor yuksek gecikmeli)
- `sayfaya_git()`, `sayfa_kaydet()`, `ekran_goruntusu()` metodlari

### FormDoldurucu
- DOM'da alanlari birden fazla stratejiyle bulur (name, id, placeholder, type)
- Turkce alan adi destegi: `"ad"` → `["name","firstname","first_name","ad","isim"]`
- 15+ alan adi tanimli (ad, soyad, eposta, telefon, sifre, adres, il, ilce, posta_kodu, tc_kimlik, kullanici_adi)
- JSON formatinda cagri: `TOR_FORM_DOLDUR('{"ad":"Ali","soyad":"Yilmaz"}')`

### OtomasyonAkislari
- `login()` — kullanici adi/sifre ile giris
- `kayit_ol()` — yeni uyelik formu doldur
- `siparis_ver()` — urun ekle, adres gir, siparis ver
- Otomatik submit butonu bulma (8 farkli secici dener)

## Uyarilar
- Tor cikis dugumleri Cloudflare/WAF captcha'ya takilabilir
- reCAPTCHA/hCaptcha icin harici API gerekir
- Timeout degerleri Tor icin 30-45sn olmali, 10sn yetmez

## motor.py Entegrasyonu
- 6 arac: TOR_AC, TOR_KAPAT, TOR_FORM_DOLDUR, TOR_LOGIN, TOR_KAYIT, TOR_SIPARIS
- Erken kontrol (Registry oncesi)
- TOOLSET_GRUPLARI "tor" grubunda
- Global singleton pattern (`_aktif_tor`, `_aktif_akislar`)
