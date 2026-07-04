# Karar Kayıtları

## Karar #38 — ReYMeN CLI çıktı temizliği (1. sefer)
**Tarih:** 2026-07-04
**Ne yapıldı:** session_db.py log.error→log.debug, .ReYMeN/session.db→merkez_db/session.db, _yanit_temizle filtresi, araclar_gelismis.py print→logger.debug, hyperframes_tool.py print→logger.debug
**Neden:** 3 sorun: ERROR log (FOREIGN KEY), tool print'leri, DÜŞÜN/EYLEM blokları

## Karar #39 — Session varlık kontrolü + durum.json doğrulama
**Tarih:** 2026-07-04
**Ne yapıldı:** _session_search_kaydet()'e SELECT 1 WHERE id=? kontrolü eklendi, session yoksa atla
**Neden:** Session oluşturma sessizce başarısız olursa FK hatası

## Karar #40 — Konuşma hafızası (REPL'de her mesaj sıfırlanıyor)
**Tarih:** 2026-07-04
**Ne yapıldı:**
- `_sor()` fonksiyonu artık her çağrıda **yeni** ConversationLoop oluşturmaz, global `_repl_cl` instance'ını kullanır
- `run_conversation()` sonunda `_konusma_gecmisi = list(_gecmis_mesajlar)` ile senkronize edilir
- __pycache__ tamamen temizlendi
**Neden:** `_sor()` içinde her seferinde `ConversationLoop()` yeniden oluşturuluyordu → `_konusma_gecmisi` boş. Ayrıca iki ayrı liste vardı (okuma: _konusma_gecmisi, yazma: _gecmis_mesajlar) ve senkronize değildi.

## Karar #41 — GOREV_BITTI(...) formatı temizleme
**Tarih:** 2026-07-04
**Ne yapıldı:** `_yanit_temizle()`'ye GOREV_BITTI("...") regex eklendi. İçindeki metni çıkarır, sadece kullanıcıya gösterir. Aynı fix `_yanit_temizle_repl()`'e de eklendi.
**Neden:** prompt_builder.py ReAct formatında GOREV_BITTI("yanit") kullanır. Model bu talimata uyup ham formatı döndürüyordu.
