# Keşfedilen Skill'ler — DeepSeek Model Sorgulama (kiral38)
**Tarih:** 2026-06-21
**Kaynak:** gecmis_konusmalar/kiral38_20260621_064621__DeepSeek Model Sorgulama.md

## 1. Sessiz Hata Yutmayı Düzeltme
- **Tanım:** Try/except bloklarında sessiz `except: pass` yerine loglama mekanizması (`_modul_uyar(...)`)
- **Dosyalar:** 75 dosyada 373 blok düzeltildi
- **Kullanım:** `except Exception as e: _modul_uyar(...)` pattern'i

## 2. Provider Router — Circuit Breaker
- **Tanım:** Çoklu LLM sağlayıcı yönlendirme, sağlık kontrolü, otomatik fallback
- **Dosya:** `provider_router.py`
- **Özellikler:** Circuit breaker (2 hata → 120s kara liste), fallback zinciri: local → karma → uzak API
- **Komut:** `/routing`

## 3. Kod Konsolidasyonu — Paket Yapısı
- **Tanım:** 159 .py dosyasını paketlere bölme (shim + taşıma yöntemi)
- **Paketler:** `reymen/guvenlik/`, `reymen/hafiza/`, `reymen/cereyan/`, `reymen/arac/`, `reymen/windows/`, `reymen/ag/`, `reymen/sistem/`
- **Yöntem:** Dosyayı pakete taşı → yerine `from reymen.X.Y import *` shim bırak

## 4. Windows Event Bus Sistemi
- **Tanım:** Modüller arası haberleşme için thread-safe event bus
- **Dosyalar:** `windows_events.py`, `windows_entegrasyon.py`
- **Event tipleri:** OLAY_TOR_HATA, OLAY_NISAN, OLAY_COKUS, OLAY_COZUM_UYGULANDI
- **Bağlantı şeması:** tor_otomasyonu → hata_cozucu, araclar_nisan → tor_otomasyonu, motor → cokus_raporlayici

## 5. Test Düzenleme ve Paket Yolu Yönetimi
- **Tanım:** `tests/tools/__init__.py` ile çift yönlü paket yolu (ReYMeN + Hermes referans)
- **Test taşıma:** Hermes referans testlerini `tests/hermes_reference/tools/` altına taşıma
- **Sonuç:** 243 test, 0 hata

## 6. Browser Tool Türkçe Alias Sistemi
- **Tanım:** `browser_tool.py`'de Türkçe komut alias'ları (ac→navigate, kapat→back, tikla→click)
- **Kullanım:** `islem = _alias.get(islem, islem)` pattern'i

## 7. Hermes → ReYMeN Marka Değişimi
- **Yeniden adlandırılanlar:** `.hermes_sync.sh` → `.ReYMeN_sync.sh`, `tests/hermes_reference/` → `tests/ReYMeN_reference/`, `tools/hermes_ajan.py` → `tools/reymen_ajan.py`
- **Kapsam:** 31 dosya yol referansı, 9 dosya yorum, 10 dosya marka ismi, 72 skill/kaynak dosyası
- **Dokunulmayanlar:** `hermes_cli` import'ları, `agent/` yedekleri, `venv/` paketleri

## 8. Shim Oluşturucu
- **Tanım:** Taşınan dosyalar için geriye dönük uyumluluk shim'leri
- **Kullanım:** Eski `from guardrails import X` → yeni `reymen.guvenlik.guardrails` modülüne yönlendirir

## 9. Güncelleme Sistemi (.ReYMeN_sync.sh)
- **Tanım:** Upstream Hermes Agent ile sync, 27 protected dosya koruması
- **Özellikler:** `--sync`, `--diff`, `--reset` parametreleri
- **Protected dosyalar:** main.py, beyin.py, motor.py, guardrails.py, hata_cozucu.py, tor_otomasyonu.py + 21 dosya daha
