
> **Kategori:** Kod

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Web Tetikleyici Sistemi_References_Test Sonuclari |
| **Nerede?** | Kod/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# Web Tetikleyici Test Sonuçları

## 5 Senaryo Testi (2026-06-21)

```
SENARYO                                  ATESLENDI?      SEBEP                                     PUAN
----------------------------------------------------------------------------------------------------
selam_merhaba_test                  (hata=0) ✅ ATESLENDI     T1: Hafiza bos                            1.00
nmap_port_tarama_test               (hata=3) ✅ ATESLENDI     T3: 3 hata                                0.30
python_nmap_video_ogrenme           (hata=0) ✅ ATESLENDI     T5: Celiski - iki kaynak farkli           0.60
```

## Detaylı Testler

### TEST 1: T1 — Hafıza Boş
- Hedef: `selam_merhaba_test` (hiç kayıt yok)
- Sonuç: ✅ ATEŞLENDİ → T1: Hafiza bos
- Aksiyon: Direkt web'e git

### TEST 2: T2 — Güven Düşük
- Hedef: `bilinmeyen_hata_test` (yok, gormez)
- Sonuç: ❌ ATEŞLENMEDİ (kayıt yok)
- Not: T2 sadece var olan ama guven<0.5 kayıtlarda ateşlenir

### TEST 3: T3 — Görev Başarısız (3 hata)
- Hedef: 3 hata
- Sonuç: ✅ ATEŞLENDİ → T3: 3 hata
- Aksiyon: Web'de çözüm ara

### TEST 4: T4 — Geçerlilik Aşmış
- Hedef: `nmap_port_tarama_test` (gecerlilik=2026-12-18)
- Sonuç: ❌ ATEŞLENMEDİ (henüz gecerli)
- Not: 2026-12-18'den sonra ateşlenecek

### TEST 5: T5 — Çelişki
- Hedef: Hafizada "yavas", videoda "hizli" → farklı
- Sonuç: ✅ ATEŞLENDİ → T5: Celiski
- Aksiyon: Web'de hakem ara

## Toplu Test

```
yeni_tool_bilinmiyor                       ✅ WEB      | T1: Hafiza bos                           | puan=1.00
nmap_port_tarama_test                      ✅ WEB      | T3: 3 hata                               | puan=0.30
python_nmap_video_ogrenme                  ✅ WEB      | T5: Celiski - iki kaynak farkli          | puan=0.60
yeni_tool_bilinmiyor                       ✅ WEB      | T1: Hafiza bos                           | puan=1.00
```

## Veritabanı

`ogrenmeler` tablosuna `web_arama_sebebi TEXT DEFAULT ''` kolonu eklendi.
