---
name: belirsiz-gorev-cozumu
description: BELİRSİZ GÖREV GELDİ
title: Belirsiz Gorev Cozumu
version: 1.0.0
---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | AI/ML mühendisi |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | AI/ML görevi gerektiğinde |
| **Neden?** | standardize etmek için |
| **Nasıl?** | Skill adımlarını takip ederek |

bul, ona göre öneri sun.
# Belirsiz Görev Çözümü

## Akış

```
BELİRSİZ GÖREV GELDİ
  ↓
1. HAFIZAYI KONTROL ET
   ├── once_hafiza.ara() → hafıza DB'sinde benzer kayıt
   │   - Anahtar kelimeleri çıkar
   │   - Kategori frekansı hesapla
   ├── session_search() → geçmiş konuşmalar
   └── .ReYMeN/kazanimlar.md → tüm ajanların ortak kaydı (Hermes `memory()` KULLANMA)
  ↓
2. EN ALAKALI KATEGORİYİ BUL
   ├── En çok eşleşen kategori
   ├── En yüksek güven skorlu kayıt
   └── Son kullanım tarihi
  ↓
3. KULLANICIYA ÖNER
   ├── "X dedin. Hafızamda en çok Y ile ilgili kayıtlarım var."
   ├── "Z'den başlayalım mı?" (tek seçenek öner)
   └── clarify() ile onay al (max 2 seçenek)
  ↓
4. ONAY ALINDI → UYGULA
   └── HAYIR → farklı kategori dene veya açık uçlu sor
```

## Keyword → Kategori Eşleme Tablosu

| Kategori | Tetikleyici Kelimeler |
|:---------|:----------------------|
| kali/network/nmap | güvenli, port, tarama, nmap, ağ, servis, pentest |
| kali/web | web, site, sql, xss, burp |
| cross-platform/security | koordinasyon, inter-agent, güvenlik, engelle |
| windows/terminal/network | windows, ipconfig, netstat, firewall |
| windows/terminal/system | systeminfo, tasklist, servis |
| dron | dron, drone, uçur, px4, uav |
| cad | cad, solidworks, çizim, 3d |
| video/python/nmap | video, python, nmap, öğren |

**Puan = kelime_eslesme(x0.3) + hafiza_guven(x0.7)**

## Kurallar

1. ASLA 4 seçenek sunma — clarify()'de max 2 choices
2. ASLA hafızayı kontrol etmeden soru sorma (once_hafiza.ara())
3. ASLA "Ne yapmak istiyorsun?" gibi açık uçlu soruyla başlama
4. Kullanıcı "hayır" derse -> 1 kez daha farklı kategori dene, yine hayir -> açık uçlu sor
5. Tahmin yanlış çıkarsa -> özür dileme, direkt "Ne yapmak istemiştin?" diye sor
6. Çok fazla kategori eşleşirse -> en yüksek guven_skoru + en yeni son_kullanim

## Hafıza Önceliği

`once_hafiza.ara()` → `session_search()` → `.ReYMeN/kazanimlar.md`

**ÖNEMLİ:** Hermes `memory()` tool'unu kullanma. AppData/.../kiral38/memories/ yoluna yazar — diğer ajanlar (Kali, Windows, CAD) erişemez. Tüm ajanlar `.ReYMeN/kazanimlar.md`'ye yazar.
