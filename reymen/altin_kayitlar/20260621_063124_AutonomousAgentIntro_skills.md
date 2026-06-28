# Keşfedilen Skill'ler — Autonomous Software Agent Introduction (reymen)
**Tarih:** 2026-06-21
**Kaynak:** gecmis_konusmalar/reymen_20260621_063124__Autonomous Software Agent Introduction.md

## 1. Hermes vs ReYMeN Karşılaştırma Standardı
- **Tanım:** Kullanıcı değerlendirmesinden çıkarılan 4 kural: güncellik, derinlik, objektiflik, bağlam
- **Skill adı:** `reymen-karsilastirma-standardi`
- **Puanlama kuralı:** Verdiğin puandan başlangıçta -3 çıkar, atlanan/yanlış başına -1 ekle
- **Kritik kural:** Önce kodda doğrula (`search_files`, `grep`, `read_file`), sonra "yok" de

## 2. Canlı Veri Cevap Formatı
- **Tanım:** Fiyat/veri sorgularında 4 adımlı format
  1. Canlı kaynak tara (web_search/web_extract)
  2. URL göster
  3. Fiyat uyumu yorumu (✅ tutarlı / ❌ farklı)
  4. Pronto cevap
- **Örnek:** Altın ons fiyatı sorgusu — 3 kaynaktan veri al, karşılaştır, ortalama ver

## 3. Delegate/Alt Ajan Loop Detector (Döngü Dedektörü)
- **Tanım:** `alt_ajan.py` içinde aynı gözlem/eylem 3x tekrarını tespit edip force bitiren mekanizma
- **Yöntem:** Sliding window (son 5) + repeat threshold (3) — set tek elemanlıysa döngü
- **Kullanım:** `LoopDetector.step(gozlem, eylem)` her eylem sonrası çağrılır
- **5N1K Görev Tanımı:** Claude Code'a verilmek üzere hazırlandı

## 4. ReYMeN Cevap Kalitesi Metodolojisi
- **Skill adı:** `reymen-cevap-kalitesi`
- **7 Aşama:**
  1. Skill Yükle
  2. Ham Veri Topla (Paralel)
  3. İşle/Kıyasla (execute_code)
  4. Görselleştir
  5. Boşlukları Bul
  6. Sentezle + Puanla
  7. Öner + Rapor
- **Dürüstlük kuralı:** Bilmiyorsan kontrol et, uydurma özür üretme

## 5. Gateway Kalite İyileştirme
- **Skill adı:** `reymen-gateway-kalite`
- **Bileşenler:**
  - TelegramRateLimiter — token bucket (30 msg/sn limiti)
  - AutoReconnector — exponential backoff
  - SessionManager — her kullanıcıya ayrı session
  - CrashRecovery — otomatik restart + admin bildirim

## 6. ReYMeN Başlangıç Durumu (reymen-baslangic)
- **Skill adı:** `reymen-baslangic`
- **Takip edilen özellikler:** MCP, SOUL.md/Personality, Context Files, Voice Mode, Terminal Backends, Memory, Skills, Toolsets, Command Approval, Browser Automation

## 7. Alt Ajan Yönetimi (alt_ajan.py)
- **Sınıflar:** `AltAjan`, `AltAjanYoneticisi`
- **Özellikler:** Thread-based çalışma, izinli araç seti (frozenset), döngü dedektörü, retry mekanizması, zaman aşımı
- **İzinli araçlar:** KOMUT_CALISTIR, PYTHON_CALISTIR, DOSYA_YAZ, DOSYA_OKU, HAFIZA_ARA, IC_GOZLEM, GOREV_BITTI, WEB_ARA, TARAYICI_AC, PDF_OKU, EXCEL_OKU, CSV_OKU, GORUNTU_ANALIZ, DOSYA_ANALIZ, PROJE_TARA, SKILL_ARA

## 8. Derinlemesine Piyasa Analizi
- **Tanım:** Altın ons fiyatı için çoklu kaynak, teknik analiz, performans, karşılaştırmalı piyasalar
- **Kaynaklar:** Investing.com, Bigpara, Bloomberg HT
- **Format:** Canlı fiyat → günlük veriler → teknik analiz → performans → karşılaştırmalı piyasalar → altın türleri → gündem → önümüzdeki hafta
