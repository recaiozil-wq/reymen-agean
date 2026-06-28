# Teknik Bilgi — Autonomous Software Agent Introduction (reymen)
**Tarih:** 2026-06-21
**Kaynak:** gecmis_konusmalar/reymen_20260621_063124__Autonomous Software Agent Introduction.md

## Hermes Agent Mimarisi (Upstream)
- **Agent core:** `run_agent.py` (tek döngü)
- **Prompt builder:** `prompt_builder.py`
- **Model router:** Model Router + Credential Pool
- **Tool registry:** `tools/registry.py`
- **İki tasarım ilkesi:**
  1. Per-conversation prompt caching sacred — her şey bundan ödün vermez
  2. Core narrow waist, capability at edges — yeni tool eklemek yüksek bar

## ReYMeN Mimarisi (Fork)
- **4 katmanlı loop:** Beyin → Motor → Steering → Learning
- **Prompt:** `prompt_assembly.py` + SOUL
- **Model:** Beyin (çok sağlayıcılı fallback)
- **Tool:** `tool_registry.py` + `motor.py`

## Hermes vs ReYMeN Karşılaştırma Puanları
| Kategori | Hermes | ReYMeN |
|----------|:------:|:------:|
| Çekirdek Mimarisi | 8/10 | 7/10 |
| ReAct Loop | 9/10 | 8/10 |
| Hafıza | 6/10 | 9/10 |
| Öğrenme | 5/10 | 9/10 |
| Güvenlik | 7/10 | 9/10 |
| Delegasyon | 9/10 | 4/10 |
| Cron | 9/10 | 1/10 |
| Platform | 9/10 | 3/10 |
| Öz Yansıma | 5/10 | 8/10 |
| Test Kapsamı | 9/10 | 6/10 |
| **TOPLAM** | **85/110** | **72/110** |

## ReYMeN'in Güçlü Yanları
1. Otomatik Öğrenme (beceri kristalleştirme) — Hermes'te yok
2. Hafıza Derinliği — 51K satır, 9 tablo, 3 hafıza türü
3. 4 Katman Güvenlik — Tirith+Threat+Anayasa+Redact
4. Reflexion Motoru — Kendi çıktısını analiz edip iyileştirir
5. 5 Katmanlı Steering Loop — Structured control
6. Windows Derinliği — SAPI TTS, WSL, PowerShell fallback
7. Tam Türkçe — Arayüz, hata mesajları, dokümantasyon

## En Kritik Eksikler
1. Cron Sistemi — Periyodik işler, raporlar
2. Native Function Calling — Regex hata üretebilir
3. Checkpoints/Rollback — Dosya değişiklikleri geri alınamaz
4. Test Coverage — 592 vs 25.000

## Delegasyon Karşılaştırması (Hermes 53/60 vs ReYMeN 29/60)
| Özellik | Hermes | ReYMeN |
|---------|--------|--------|
| Batch/Parallel Tasks | ✅ 3 task aynı anda | ❌ Tek tek sıralı |
| Background Async | ✅ Sonuç konuşmaya döner | ❌ Thread'de kalır |
| Orchestrator Rolü | ✅ Nested delegate | ❌ Zincir engelli |
| İzole Terminal | ✅ Her subagent ayrı shell | ❌ Aynı Motor state |
| Per-task Toolsets | ✅ İhtiyaca göre ayrı set | ❌ Sabit izinli araçlar |
| Sonuç Doğrulama | ✅ Verifiable handle | ❌ LLM sözüne güven |

## Alt Ajan (alt_ajan.py) Detayları
- **717 satır**
- `AltAjan` sınıfı: Her görev için yeni instance, thread-local marker ile ana ajandan izole
- `AltAjanYoneticisi`: Görev havuzu, callback sistemi, retry mekanizması
- **İzinli araçlar (15):** KOMUT_CALISTIR, PYTHON_CALISTIR, DOSYA_YAZ, DOSYA_OKU, HAFIZA_ARA, IC_GOZLEM, GOREV_BITTI, WEB_ARA, TARAYICI_AC, PDF_OKU, EXCEL_OKU, CSV_OKU, GORUNTU_ANALIZ, DOSYA_ANALIZ, PROJE_TARA, SKILL_ARA
- **Döngü Dedektörü:** Son 5 gözlem/eylem takibi, 3x tekrar → force bitir
- **Zaman aşımı:** ALT_AJAN_ZAMAN_ASIMI=120s (global env var)

## Altın Ons Piyasa Verileri (21 Haziran 2026)
- **Anlık fiyat:** ~$4.155
- **Kaynaklar:** Investing.com ($4.160), Bigpara ($4.155), Bloomberg HT ($4.155)
- **Günlük değişim:** -1,28% ila -1,29%
- **Gün aralığı:** $4.120 — $4.213
- **52 hafta aralığı:** $3.247 — $5.595
- **Teknik:** Güçlü Sat sinyali (tüm zaman dilimlerinde)
- **Aylık değişim:** -%8,45
- **Gram altın:** ₺6.205

## ReYMeN Skill'leri (Kayıtlı)
1. `reymen-baslangic` — Başlangıç durumu yükleme
2. `reymen-cevap-kalitesi` — 7 aşamalı cevap metodolojisi
3. `reymen-gateway-kalite` — Gateway iyileştirme
4. `reymen-karsilastirma-standardi` — Karşılaştırma standardı
