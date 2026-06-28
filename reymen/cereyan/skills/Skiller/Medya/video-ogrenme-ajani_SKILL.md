---
name: video-ogrenme-ajani
title: Video Öğrenme Ajanı
description: YouTube/Video'dan skill çıkarma pipeline'ı — transcript al, bölümle, hafızayla karşılaştır, hata tespit et, birleşik skill kaydet.
tags: [video, learning, youtube, yt-dlp, oncehafiza]
---


> **Kategori:** Medya

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Video ajanı |
| **Ne?** | YouTube/Video'dan skill çıkarma pipeline'ı — transcript al, bölümle, hafızayla karşılaştır, hata tespit et, birleşik skill kaydet. |
| **Nerede?** | Medya/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Video Öğrenme Ajanı

## Pipeline

```
YouTube URL
  ↓
① yt-dlp ile video bilgisi + altyazı indir
  ├─ Altyazı varsa → direkt transcript
  └─ Altyazı yoksa → Whisper ile ses → metin
                      ↓
② Metni bölümlere ayır:
  ├─ Giriş (amaç, hedef kitle)
  ├─ Teknik adımlar (kod, komut, konfigürasyon)
  └─ Sonuç/özet (çıktılar, hata çözümleri)
                      ↓
③ Her bölümden skill çıkar:
  ├─ Kod bloğu → ayrı kayıt
  ├─ Komut → ayrı kayıt
  └─ Kavram → ayrı kayıt
                      ↓
④ Hafızadaki eski bilgiyle karşılaştır:
  ├─ Tekrar eden bilgi → basari++ (güven artar)
  ├─ Çelişen bilgi → uyarı + ikisini de tut
  ├─ Yeni bilgi → ekle
  └─ Eksik bilgi (hafızada var, videoda yok) → not et
                      ↓
⑤ Hata tespit et:
  ├─ Web'den (resmi doküman) API doğrula
  ├─ Hafızadan (eski doğru bilgi) karşılaştır
  └─ Mantıksal (parse edilmemiş sonuç, eksik try/except)
                      ↓
⑥ Birleşik skill kaydet:
  kategori: video/<dil>/<konu>
  cross-ref: <eski_kategori> (ör: kali/network/nmap)
```

## Örnek: "Python ile nmap kullanımı" Videosu

```
Video Adımları:
1. pip install python-nmap
2. import nmap
3. nm = nmap.PortScanner()
4. nm.scan("127.0.0.1", "22-443")

Hafıza Karşılaştırması:
- kali/network/nmap (ID=12, guven=1.0) → CLI bilgileri mevcut
- python-nmap kütüphanesi → YENİ (videodan öğren)

Hata Tespiti:
- nm.scan("127.0.0.1", "22-443") → port range DOĞRU (PyPI onaylı)
- EKSİK: try/except PortScannerTimeout yok
- EKSİK: arguments="-sV" versiyon tespiti yok
- EKSİK: sonuç parse edilmemiş (dict işlenmemiş)

Düzeltilmiş Kod:
- try/except eklendi
- arguments ile versiyon tespiti
- sonuç parse
```

## Kategori Yapısı

video/<dil>/<konu>
video/learning (mimari)

## Cross-Reference

Her video skill'i, eski kategoriyle cross-ref içerir:
video/python/nmap ↔ kali/network/nmap
video/python/requests ↔ kali/web
