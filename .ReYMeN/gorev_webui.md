# Web UI — ReYMeN Dashboard Geliştirme

## NE
ReYMeN'in web arayüzünü Hermes Web UI seviyesine çıkar.

## MEVCUT DURUM
- `dashboard/app.py` var (basit dashboard)
- Eksik: görev takibi, log görüntüleme, öğrenme istatistikleri, session search

## YAPILACAKLAR

### 1. Dashboard'u Geliştir
- `dashboard/app.py`'yi FastAPI ile güncelle
- Şu sayfaları ekle:
  - Ana sayfa: sistem durumu, son aktivite
  - Görevler: çalışan/bitmiş görev listesi
  - Loglar: run_log.jsonl + fail_log.jsonl görüntüleme
  - Öğrenme: hafızadaki çözüm sayısı, TTL durumu
  - Session search: geçmiş arama

### 2. API Endpoint'leri
- `GET /api/durum` — sistem durumu
- `GET /api/istatistik` — öğrenme istatistikleri
- `GET /api/loglar` — son loglar
- `POST /api/session-ara` — session search
- `POST /api/gorev-baslat` — görev başlat

### 3. Frontend
- Koyu tema (Hermes ile uyumlu)
- Mobil uyumlu
- Canlı güncelleme (SSE veya polling)

## KISITLAMALAR
- shell=True KULLANMA
- Mevcut dashboard/app.py'yi koru, yeni dosya ekle
- Hata alırsan düzeltip tekrar dene (max 3)
