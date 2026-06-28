---
name: autonomous-ai-agents_takili-kalma_references_kurtarma-akisi
description: İki Taraflı Kurtarma Akışı
title: "Autonomous Ai Agents Takili Kalma References Kurtarma Akisi"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | İki Taraflı Kurtarma Akışı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# İki Taraflı Kurtarma Akışı

## Mimari
Bu sistem iki ayrı Hermes session'ı arasında çalışır:

| Session | Konum | Yetenekler |
|---------|-------|------------|
| **Local Hermes** | Bilgisayar (Windows, MINGW64 terminal) | Terminal, dosya işlemleri, yerel çalıştırma, **Tor Browser (hermestor.py)**, web_search, web_extract |
| **Telegram Hermes** | Bulut (bu session) | Tor Browser, web_search, web_extract, cron job |

**ÖNEMLİ:** Local Hermes terminal'i MINGW64 üzerinde Windows'ta çalışır — Python script'leri doğrudan çalıştırabilir.
`hermestor.py` script'i Tor Browser'ı kontrol eder, bu nedenle local Hermes de Tor'da arama yapabilir.

## Kurtarma Akışı (Local → Önce Kendi Çöz → Telegram)

```
Local Hermes takılır
  → Adım tekrarı (2 kez) çözmezse
  → Todo döngüsü koruması çözmezse
  → Model değişimi çözmezse
  → 5. Kendin Araştır aşaması:
     1. web_search (varsa normal web araması)
     2. python /c/Users/marko/hermestor.py search "sorgu" (Tor ile)
     3. Sonuçları oku, çözüm dene
     4. Max 3 farklı sorgu
  → Hâlâ çözüm yoksa:
     → takildi.txt oluşturur (C:\Users\marko\takildi.txt)
     → Telegram Hermes cron job'u dosyayı bulur (her 15 dk)
     → Tor'da daha derin araştırma yapar
     → Çözümü Telegram'a bildirir
     → takildi.txt silinir
```

## Cron Job Detayı

- **Job adı:** Takilma-Izleyici
- **Sıklık:** Her 15 dakika
- **Çalıştığı yer:** Telegram Hermes
- **Tetikleyici:** `C:\Users\marko\takildi.txt` dosyasının varlığı
- **Yüklü skill:** tor-browser-arama
- **Sadece dosya VARSA** Tor'da araştırma yapılır (boş kontrollerde minimum token tüketimi)
- **Dosya içeriği formatı:**
  ```
  SORUN: <kısa hata/ne yapmaya çalıştığın>
  ADIM: <takıldığın adım>
  DENENEN: <denenen çözümler>
  ANAHTAR_KELIMELER: <Tor'da denenen sorgular>
  ```

## Önemli Notlar

1. Local Hermes hem web_search (varsa) hem de Tor (hermestor.py) kullanabilir
2. `hermestor.py search` DuckDuckGo HTML endpoint'ini kullanır — bazen sonuç döndürmez (Tor IP bloklaması, endpoint değişikliği)
3. DuckDuckGo sonuç döndürmezse alternatif arama yöntemleri kullanılabilir:
   - Google'a proxy üzerinden GET isteği
   - Bing'e proxy üzerinden GET isteği
   - Wikipedia sorgusu
4. Cron job boş kontrollerde neredeyse hiç token tüketmez (sadece "dosya yok" cevabı)
5. Takılma anında gerçek araştırma yapılırsa normal bir sohbet maliyeti kadar token gider
