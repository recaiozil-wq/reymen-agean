---
skill_id: 4aa1e54ff549
usage_count: 1
last_used: 2026-06-16
---
# İki Taraflı Kurtarma Akışı

## Mimari
Bu sistem iki ayrı ReYMeN session'ı arasında çalışır:

| Session | Konum | Yetenekler |
|---------|-------|------------|
| **Local ReYMeN** | Bilgisayar (Windows, MINGW64 terminal) | Terminal, dosya işlemleri, yerel çalıştırma, **Tor Browser (hermestor.py)**, web_search, web_extract |
| **Telegram ReYMeN** | Bulut (bu session) | Tor Browser, web_search, web_extract, cron job |

**ÖNEMLİ:** Local ReYMeN terminal'i MINGW64 üzerinde Windows'ta çalışır — Python script'leri doğrudan çalıştırabilir.
`hermestor.py` script'i Tor Browser'ı kontrol eder, bu nedenle local ReYMeN de Tor'da arama yapabilir.

## Kurtarma Akışı (Local → Önce Kendi Çöz → Telegram)

```
Local ReYMeN takılır
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
     → Telegram ReYMeN cron job'u dosyayı bulur (her 15 dk)
     → Tor'da daha derin araştırma yapar
     → Çözümü Telegram'a bildirir
     → takildi.txt silinir
```

## Cron Job Detayı

- **Job adı:** Takilma-Izleyici
- **Sıklık:** Her 15 dakika
- **Çalıştığı yer:** Telegram ReYMeN
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

1. Local ReYMeN hem web_search (varsa) hem de Tor (hermestor.py) kullanabilir
2. `hermestor.py search` DuckDuckGo HTML endpoint'ini kullanır — bazen sonuç döndürmez (Tor IP bloklaması, endpoint değişikliği)
3. DuckDuckGo sonuç döndürmezse alternatif arama yöntemleri kullanılabilir:
   - Google'a proxy üzerinden GET isteği
   - Bing'e proxy üzerinden GET isteği
   - Wikipedia sorgusu
4. Cron job boş kontrollerde neredeyse hiç token tüketmez (sadece "dosya yok" cevabı)
5. Takılma anında gerçek araştırma yapılırsa normal bir sohbet maliyeti kadar token gider
