# Alınan Kararlar — Autonomous Software Agent Introduction (reymen)
**Tarih:** 2026-06-21
**Kaynak:** gecmis_konusmalar/reymen_20260621_063124__Autonomous Software Agent Introduction.md

## Karar 1: Karşılaştırma Standardı Oluşturma
- **Ne yapıldı:** reymen-karsilastirma-standardi skill'i oluşturuldu
- **Neden:** Önceki Hermes vs ReYMeN karşılaştırmasında %31 doğruluk oranı (%31 → %100 düzeltildi)
- **Kural:** Önce canlı doküman oku (web_extract), sonra cevap ver

## Karar 2: Canlı Veri Formatı
- **Ne yapıldı:** Fiyat/veri sorgularında standart 4 adımlı format
- **Neden:** Kullanıcı "bu formatta cevap ver" dedi
- **Format:** Kaynak+URL → fiyat tablosu → uyum yorumu → ortalama

## Karar 3: Döngü Dedektörü Implementasyonu
- **Ne yapıldı:** `alt_ajan.py`'da Loop Detector — aynı gözlem/eylem 3x tekrarı → force GOREV_BITTI
- **Neden:** LLM takılması durumunda 90 tur × API call = $$$ token israfı
- **Yöntem:** Sliding window (son 5) + tekrar eşiği (3)
- **5N1K:** Claude Code'a görev tanımı olarak hazırlandı

## Karar 4: ReYMeN Kendini Konumlandırma
- **Ne yapıldı:** Hermes'e bağımlılık vurgusu kaldırıldı, "ReYMeN ajanı" olarak tanımlandı
- **Neden:** Kullanıcı "Hermes agent altyapısı üzerine calisan kaldir" dedi

## Karar 5: Cevap Kalitesi Metodolojisi
- **Ne yapıldı:** 7 aşamalı metodoloji oluşturuldu
- **Neden:** Kullanıcı "daha derinlemesine olsun" dedi
- **Kural:** Her soruda önce araç kullan (web_search/execute_code), sonra cevap ver

## Karar 6: RPG Sorusu Çözüm Yaklaşımı
- **Ne yapıldı:** Basit kuralları oku → brute force hesapla → direkt cevap ver
- **Hata:** Kafadan n² formülü uyduruldu, execute_code ile brute force yapılmalıydı
- **Ders:** Önce veriyi/kuralları topla, yorum katma, direkt cevap ver

## Karar 7: Gateway Kalite İyileştirmeleri
- **Ne yapıldı:** Rate limiter, auto-reconnect, session manager, crash recovery
- **Neden:** GitHub'a yükleme öncesi kullanıcıların sorun yaşamaması için
