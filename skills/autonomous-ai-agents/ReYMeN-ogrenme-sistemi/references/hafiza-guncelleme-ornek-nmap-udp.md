# Hafıza Güncelleme Örneği: nmap UDP Tarama

**Tarih:** 2026-06-21
**Hedef:** ID=12 (kali/network/nmap) — `nmap_port_tarama_test`

## Eski Kayıt

```sql
-- ID=12, basari=1, hata=0, guven=1.0
icerk: "nmap ile port tarama: -sV servis versiyon, -sT TCP, -sU UDP icin"
```

## Web'den Toplanan Yeni Bilgiler

| Kaynak | URL | Güven |
|--------|-----|-------|
| Nmap.org (resmi) | https://nmap.org/book/scan-methods-udp-scan.html | ★★★★★ |
| Security SE | https://security.stackexchange.com/q/52566 | ★★★★☆ |
| Netlas Blog (2025) | https://netlas.io/blog/nmap_commands/ | ★★★☆☆ |

## Karşılaştırma

| Alan | Eski | Yeni | Çatışma? |
|:-----|:-----|:-----|:---------|
| `-sU` kullanımı | Sadece "UDP için" | Detaylı: `-sUV`, `open\|filtered` sorunu | Eksik ✅ |
| Hızlandırma | Yok | `--min-rate`, `--max-retries`, `--defeat-icmp-ratelimit` | Eksik ✅ |
| İki aşamalı tarama | Yok | Stage 1 sweep → Stage 2 version scan | Eksik ✅ |
| Kaynak | Yok | 3 URL + tarih | Eksik ✅ |

## Çatışma Çözümü: UPDATE (append)

```python
# Eski bilgi dogru ama eksik → silme, overwrite degil, APPEND
yeni_icerik = eski_icerik + """
=== UDP Scan (2025 Best Practices) ===
-sUV : UDP + versiyon tespiti
--min-rate 5000 : minimum paket hizi
--defeat-icmp-ratelimit (Nmap 7.40+)
...

=== Kaynaklar ===
[1] https://nmap.org/book/scan-methods-udp-scan.html
[2] https://security.stackexchange.com/q/52566
"""

con.execute("""
    UPDATE ogrenmeler SET 
        icerik = ?,
        guven_skoru = ?,
        basari_sayisi = basari_sayisi + 1,
        son_kullanim = date('now'),
        guncelleme = datetime('now')
    WHERE id = ?
""", (yeni_icerik, 1.0, 12))
# Kayit sayisi DEGISMEDI: ayni ID=12
```

## Neden Silmedik / Yenisi Oluşturmadık?

| Aksiyon | Uygun mu? | Gerekçe |
|:--------|:----------|:--------|
| SİL | ❌ Hayır | Eski bilgi yanlış değil |
| OVERWRITE | ❌ Hayır | Eski bilginin tamamı gerekli |
| YENİ KAYIT AÇ | ❌ Hayır | Aynı konuda 2 kayıt = kafa karışıklığı |
| **APPEND (UPDATE)** | **✅ Evet** | Eski korunur, yeni eklenir, basari++ |

## Son Durum

- ID=12 (aynı)
- icerik 50 → 1328 karakter (26x genişledi)
- basari 1 → 2
- guven 1.0 (korundu)
- toplam kayıt sayısı: değişmedi
- LLM atlama: ✅ guven=1.0 > 0.8 → sıfır maliyet
