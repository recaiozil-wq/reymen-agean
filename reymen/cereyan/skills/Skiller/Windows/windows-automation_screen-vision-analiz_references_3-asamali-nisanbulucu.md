
> **Kategori:** Windows

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Windows ajanı |
| **Ne?** | Windows Automation_Screen Vision Analiz_References_3 Asamali Nisanbulucu |
| **Nerede?** | Windows/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# 3 Asamali Hiyerarsik Ekran Hedef Bulma (NisanBulucu)

## Konsept

Ekranda bir UI elemanini bulmak icin 3 asamali kademeli strateji:

1. **DOM (Selenium)** — `find_element` ile HTML lokatoru dene
2. **Gorsel Sablon (OpenCV)** — `.ReYMeN/nisanlar/` klasorundeki .png ile eslestir
3. **Metin OCR (pytesseract)** — Ekrani OCR ile tara, metni bul

## Ne Zaman Kullanilir

- `TOR_FORM_DOLDUR` DOM'da alan bulamazsa otomatik fallback
- CAPTCHA/WAF blokajinda form alani tespiti
- Dinamik class/id kullanan sitelerde sablon eslestirme
- Tesseract OCR ile etiket metni bulma

## Modul

`araclar_nisan.py` (ReYMeN projesinde) — `NisanBulucu` sinifi

```python
bulucu = NisanBulucu(guven_esigi=0.75)
sonuc = bulucu.bul("giris_buton", driver=tor_driver, metin_alternatif="Giris Yap")
# -> {"asama": 1, "x": 100, "y": 200, "guven": 1.0, "metin": "Giris Yap", "element": ...}
```

## Bilinen DOM Lokatorlari

| Sablon Adi | DOM XPath Secicileri |
|-----------|---------------------|
| `giris_buton` | `//button[@type='submit']`, `//input[@type='submit']`, `//button[contains(text(),'Giriş')]` |
| `kayit_buton` | `//a[contains(text(),'Kayıt')]`, `//button[contains(text(),'Register')]` |
| `captcha_kutu` | `//iframe[contains(@src,'recaptcha')]`, `//div[@class='g-recaptcha']` |
| `onay_kutusu` | `//input[@type='checkbox']`, `//*[@role='checkbox']` |
| `ad_alani` | `//input[@name='ad']`, `//input[@name='firstname']` |
| `soyad_alani` | `//input[@name='soyad']`, `//input[@name='lastname']` |
| `eposta_alani` | `//input[@type='email']`, `//input[@name='email']` |
| `sifre_alani` | `//input[@type='password']` |
| `adres_alani` | `//textarea[@name='adres']`, `//textarea[@name='address']` |
| `telefon_alani` | `//input[@type='tel']`, `//input[@name='phone']` |

## Gorsel Sablon .png Dosyalari

`.ReYMeN/nisanlar/` klasorune konur. Dosya adi sablon adiyla eslesir:

```
.ReYMeN/nisanlar/
  giris_buton.png   # "giris_buton" icin aranir
  captcha_kutu.png  # "captcha_kutu" icin aranir
  ...
```

- OpenCV `matchTemplate` ile taranir
- Varsayilan guven esigi: %75 (`guven_esigi=0.75`)
- cozunurlukten bagimsiz calisir (gozlenen + sablon ayni olcekli olmali)

## Kullaniciya Oneri

Hedef siteden ekran goruntusu al:

```python
with mss.mss() as sct:
    mon = sct.monitors[1]
    img = sct.grab(mon)
    mss.tools.to_png(img.rgb, img.size, output=".ReYMeN/nisanlar/giris_buton.png")
```

Sonra `.png` dosyasini kIrp (sadece buton bolgesini birak).
