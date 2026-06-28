# Alınan Kararlar — DeepSeek Model Sorgulama (kiral38)
**Tarih:** 2026-06-21
**Kaynak:** gecmis_konusmalar/kiral38_20260621_064621__DeepSeek Model Sorgulama.md

## Karar 1: Sessiz Except Yasak
- **Ne yapıldı:** 373 try/except bloğu `except: pass` → `except Exception as e: _modul_uyar(...)`
- **Neden:** Sessiz hata yutma, hata ayıklamayı imkansız hale getiriyordu
- **Alternatif:** Hataları tamamen görmezden gelmek (reddedildi)

## Karar 2: Kök/Agent Ayrımı
- **Ne yapıldı:** ReYMeN özel dosyalar kökte, Hermes orijinalleri `agent/` klasöründe
- **Neden:** Fork koruması ve güncelleme kolaylığı
- **Alternatif:** Tümünü aynı klasörde tutmak (reddedildi - çakışma riski)

## Karar 3: Override Mekanizması
- **Ne yapıldı:** 27 dosya kökteki versiyonu kullanır, `agent/` içindeki yedekler sadece referans
- **Neden:** Sync sırasında ReYMeN değişikliklerinin korunması

## Karar 4: Provider Routing — Circuit Breaker
- **Ne yapıldı:** Circuit breaker (2 hata → 120s kara liste), fallback zinciri: local → karma → uzak API
- **Neden:** Bir sağlayıcı düştüğünde otomatik olarak diğerine geçmek
- **Sağlayıcılar:** deepseek (deepseek-v4-flash), groq (llama-3.1-8b-instant), openai (gpt-4o-mini), lmstudio

## Karar 5: Windows Otomasyon Entegrasyonu — Event Bus
- **Ne yapıldı:** `windows_events.py` + `windows_entegrasyon.py` ile merkezi event sistemi
- **Neden:** Modüller arası gevşek bağlı haberleşme (tor_otomasyonu, hata_cozucu, motor, cokus_raporlayici)
- **Detay:** Thread-safe, lock-based, geçmiş kaydı (son 100 olay)

## Karar 6: Test Düzenleme Stratejisi
- **Ne yapıldı:** `tests/tools/__init__.py` çift yönlü yapıldı, Hermes reference testleri ayrıldı
- **Neden:** ReYMeN testleri kendi API'sini test etmeli, Hermes testleri referans kalmalı
- **Sonuç:** 243 test geçti, 0 hata

## Karar 7: Kod Konsolidasyonu — Shim Yöntemi
- **Ne yapıldı:** Dosyaları paketlere taşı + shim bırak (sıfır kırılma garantisi)
- **Neden:** 159 root .py dosyası dağınıktı, paket yapısı gerekiyordu
- **Sıralama:** Önce 1-2 paket dene, test et → sonra tümüne yay

## Karar 8: Hermes → ReYMeN Marka Değişimi
- **Ne yapıldı:** Tüm referanslar, dosya adları, yorumlar "Hermes" → "ReYMeN" olarak değiştirildi
- **Neden:** ReYMeN'in bağımsız bir fork olduğunu vurgulamak
- **Dokunulmayanlar:** `hermes_cli` import'ları (3. parti paket), `HERMES_HOME` env var, `agent/` yedekleri
- **Kapsam:** 100+ dosya, 243 test geçiyor

## Karar 9: Güncelleme Sistemi — .ReYMeN_sync.sh
- **Ne yapıldı:** Upstream Hermes Agent sync script'i, 27 protected dosya
- **Neden:** Fork'un güncel kalması ama ReYMeN özel değişikliklerin korunması
