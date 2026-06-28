---
name: software-development_reymen-motor-arac-ekleme_references_araclar_nisan
description: araclar_nisan.py — 3 Asamali Hiyerarsik Ekran Tarayici
title: "Software Development Reymen Motor Arac Ekleme References Araclar Nisan"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | araclar_nisan.py — 3 Asamali Hiyerarsik Ekran Tarayici |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# araclar_nisan.py — 3 Asamali Hiyerarsik Ekran Tarayici

**Dosya:** `C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi\araclar_nisan.py`
**Boyut:** ~280 satir, ~11 KB

## Mimar

3 asamali fallback:
1. **DOM** — Selenium `find_element` ile lokator ara (name, id, placeholder, XPath)
2. **Gorsel Sablon** — OpenCV `matchTemplate` ile `.ReYMeN/nisanlar/*.png` eslestir
3. **Metin OCR** — pytesseract ile ekranda yazi ara

## Kullanim

```python
from araclar_nisan import NisanBulucu

bulucu = NisanBulucu(guven_esigi=0.75)

# Driver ile (Asama 1 + 2 + 3)
sonuc = bulucu.bul("giris_buton", driver=driver, metin_alternatif="Giris")
# -> {"asama": 1, "x": 500, "y": 300, "guven": 1.0, "element": WebElement}

# Driver'siz (Asama 2 + 3)
sonuc = bulucu.bul("captcha_kutu", metin_alternatif="captcha")
# -> {"asama": 3, "x": 400, "y": 200, "guven": 0.65, "metin": "captcha"}
```

## On Tanimli DOM Lokatorler

| Sablon | DOM XPath |
|--------|-----------|
| giris_buton | `//button[@type='submit']`, `//button[text()='Giriş']`, `//a[text()='Login']` |
| kayit_buton | `//a[text()='Kayıt']`, `//button[text()='Register']` |
| captcha_kutu | `//iframe[@src='recaptcha']`, `//div[@class='g-recaptcha']` |
| onay_kutusu | `//input[@type='checkbox']`, `//*[@role='checkbox']` |
| ad_alani | `//input[@name='ad']`, `//input[@name='firstname']` |
| soyad_alani | `//input[@name='soyad']`, `//input[@name='lastname']` |
| eposta_alani | `//input[@type='email']` |
| sifre_alani | `//input[@type='password']` |
| adres_alani | `//textarea[@name='adres']`, `//input[@name='address']` |
| telefon_alani | `//input[@type='tel']`, `//input[@name='phone']` |

## Nisan Sablonlari

- Dizin: `.ReYMeN/nisanlar/`
- Format: `.png`, 80x80 px onerilen
- Yakalama araci: `nisan_yakala.py`
- Guven esigi: %75 (degistirilebilir)
- Cozunurluk: Tor Browser letterboxing ile ayni cozunurlukte alinmali

## motor.py Entegrasyonu

`TOR_FORM_DOLDUR` basarisiz alanlarda otomatik tetiklenir:

```python
if sonuc["basarisiz"]:
    from araclar_nisan import NisanBulucu
    nisan = NisanBulucu()
    for alan in sonuc["basarisiz"]:
        nisan_bul = nisan.bul(alan, driver=self._tor_browser.driver, metin_alternatif=deger)
```
