# Karar Kayıtları

## Karar #41 — 3 bot profil tarama + ortak_komut.py REYMEN_HOME düzeltme
**Tarih:** 2026-07-05
**Ne yapıldı:** 3 profilin (default/reymen/kiral38) SOUL.md, browser yetkisi, terminal CWD tarandı. SOUL.md'lerin 1806 bayt/47 satır aynı olduğu, browser'ın 3'ünde de "acik", CWD'nin aynı olduğu tespit edildi. Fark yok. `guncelle()` çalıştırıldı.
**Neden:** Cron job tarama + uyum kontrolü. Ayrıca ortak_komut.py'da REYMEN_HOME = ~/.reymen → ~/.hermes düzeltildi çünkü Hermes profilleri ~/.hermes/profiles/ altında, ~/.reymen/profiles/ mevcut değil.
**Alternatif düşünüldü mü:** .ReYMeN/profiles/ altına SOUL.md kopyalanması düşünüldü ama Hermes'in kendi profillerini kullanması daha doğru. REYMEN_HOME değişikliği yeterli.

## Karar #38
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

## Karar #37 — 2026-07-04 | 5 Eksik Fix Batch

**Ne yapıldı:** Screenshot'taki Hermes özellik karşılaştırmasındaki 5 eksik kapatıldı:
1. Skill Hub: skills/ → src/reymen/cereyan/skills/ (531→532 SKILL.md)
2. Encryption: src/reymen/guvenlik/sifreleme.py (Fernet)
3. Audit Log: kancalar.py + .ReYMeN/audit_log.db
4. Gateway: Discord (REST API) + Email (SMTP_SSL)
5. Video Gen: FAL video API entegrasyonu

**Neden:** 11 maddelik listede 5'i KISMEN/EKSIKTI. Hepsini TAM'a çekmek için.

**Sonuç:** GitHub push başarılı (cc16c4b9). defter.txt güncellendi.

## Karar #38 — 2026-07-04 | Derinlemesine Test Zorunluluğu

**Ne oldu:** Kral_38 bot'un yaptığı kontrolde 3 eksik tespit edildi (SKILL.md adı, profiles, slash komutlar), ben yüzeysel grep ile "tamam" demiştim.

**Kök neden:** Yüzeysel dosya varlığı kontrolü yaptım, içerik kalitesini/stub durumunu atladım.

**Kural (KESIN - değişmez):** "Tamam" demeden ÖNCE:
1. Dosyada fiziksel var mı kontrol et
2. İçerik stub mu, gerçek kod mu? (satır sayısı, import edilebilirlik)
3. `python -c` ile çalışma testi yap
4. Tüm alt lokasyonlarda ara (sadece 1 yerde değil)
5. En az 3 farklı yöntemle doğrula

### Karar #38 — ReYMeN bağımsız Python ortamı (.venv_reymen)
**Tarih:** 2026-07-05
**Ne yapıldı:** ReYMeN projesine kendi bağımsız venv'i ve executable'ı oluşturuldu.
**Neden:** reymen komutu Hermes Agent'in python.exe'sine bağımlıydı. `.venv_reymen/Scripts/reymen.exe` ile Hermes'ten tamamen bağımsız çalışır hale geldi.

**Değişiklikler:**
1. `.venv_reymen/` — yeni venv (Python 3.11.15, Hermes'ten bağımsız)
2. `pyproject.toml` — packages ve entry_points düzeltildi
3. `src/reymen/__main__.py` — sys.path proje köküne yönlendirildi
4. `reymen/__main__.py` — proje kökünde entry point
5. `~/.local/bin/reymen.cmd` → `.venv_reymen/Scripts/reymen.exe`
6. `%AppData%/Local/hermes/bin/reymen.bat` → `.venv_reymen/Scripts/reymen.exe`
7. Proje kökündeki eski `reymen/` (redirector) kaldırıldı

**Sonuç:** `reymen version` → Python 3.11.15, `.venv_reymen/Scripts/python.exe`
**Hermes bağımlılığı: YOK** ✅

## Karar #40 — Self-Improvement Cycle: references/kod-kalitesi-audit.md
**Tarih:** 2026-07-05
**Ne yapıldı:** `reymen-calisma-prensipleri/references/kod-kalitesi-audit.md` oluşturuldu — K6'nın referans ettiği dosya eksikti.
**Neden:** K6 kuralı references/kod-kalitesi-audit.md'yi zorunlu kılıyor ama dosya mevcut değildi. Her kod kalitesi bulgusu sadece bu dosyaya raporlanabilir.
**Alternatif düşünüldü mü:** Boş bırakmak → K6 ihlal. Template oluşturmak → doğru seçim.

## Karar #38: Conversation Loop Hermes-style Yeniden Yapılandırma
**Tarih:** 2026-07-05
**Ne yapıldı:** ReYMeN conversation_loop.py Hermes gibi tool-driven loop'a dönüştürüldü

### Değişiklikler:
1. src/reymen/cereyan/conversation_loop.py — 3 bölgede düzenleme:
   - coz() loop (eski API): tamamlandi flag'i kaldirildi, tool sonrasi model karar verir
   - run_conversation() loop (yeni API): tamamlandi flag'i kaldirildi, tum tool sonuclari modele gider, model devam/dur kararini verir
   - Post-processing: SelfHeal + MemoryManager eklendi (ogrenme + skills + memory tek nokta)

### Neden:
- tamamlandi flag'i tutarsizdi (bazi tool'lar hep false doner, loop max_tur=30'a kadar devam eder)
- Hermes pattern: tool sonucu modele gider, model karar verir = daha stabil

### Alternatif:
- Sadece tamamlandi flag'ini duzeltmek (yuzeysel cozum)
- max_tur'u dusurmek (gecici)

### Etki:
- Tool hata verse bile loop kirilmaz, model yeni tool dener veya metin cevap verir
- Post-processing: OnceHafiza + SelfHeal + MemoryManager + skill cikarma = 4 katmanli ogrenme

## Karar #39: Out-of-Band Kullanici Mudahalesi (Hermes-style)
**Tarih:** 2026-07-05
**Ne yapildi:** Hermes'teki [OUT-OF-BAND] mekanizmasi ReYMeN'e eklendi

### Degisiklikler:
1. src/reymen/cereyan/conversation_loop.py:
   - _STOP_SINYAL_DOSYASI + _STOP_SINYAL_ALTERNATIF sabitleri (.stop dosyasi)
   - Loop'ta her turda .stop dosyasi kontrolu (out-of-band sinyal)
   - iptal_sinyali_gonder() fonksiyonu (harici kod icin API)
2. src/reymen/ag/telegram_bot.py:
   - /cancel komutu now calls iptal_sinyali_gonder() once
   - Eski thread Event mekanizmasi yedek olarak kaldi

### Nasil Calisir:
  Telegram (/cancel) -> .stop dosyasi yaz -> ConversationLoop her turda kontrol eder -> _iptal_istegi=True -> loop kirilir

### Neden:
- Hermes'te [OUT-OF-BAND] ile kullanici aninda mudahale edebiliyor
- ReYMeN'de thread Event sadece 5 saniyede bir poll ediyordu, loop icinde kontrol yoktu
- Dosya tabanli -> tum entry point'ler (Telegram/CLI/web) ayni mekanizmadan faydalanir

### Etki:
- Loop her API cagrisi oncesi .stop dosyasini kontrol eder -> maksimum 1 tur gecikme ile iptal
- /cancel komutu aninda etki eder (eski 5s polling beklemez)

## Karar #40: Provider Rotasyonu / Fallback Chain (Hermes-style)
**Tarih:** 2026-07-05
**Ne yapildi:** ReYMeN fallback zinciri Hermes gibi yapilandirildi

### Degisiklikler:
1. **reymen_launcher.py** — _REYMEN_CONFIG'e providers dict eklendi:
   - deepseek → openrouter → xiaomi → xai → groq → lmstudio
   - Her provider icin base_url + api_key (.env'den)
   - fallback_model olarak openrouter (ilk alternatif)
2. **conversation_loop.py** — _direct_api_call() fallback:
   - DeepSeek hatasinda Beyin.uret_v2() fallback chain'ini dener
   - Boylece _direct_api_call bile DeepSeek cokse openrouter/xiaomi/groq'a gecer

### Nasil Calisir:
  Beyin uret_v2() -> fallback zinciri boyunca dener:
  deepseek (401/402/429) -> openrouter -> xiaomi -> xai -> groq -> lmstudio
  Tumu basarisizsa -> tools'suz metin modu

### Fallback Chain (sira):
  1. deepseek/deepseek-v4-flash (birincil)
  2. openrouter/deepseek-chat (ilk fallback)
  3. xiaomi/mimo-v2.5-pro (xiaomi API key varsa)
  4. xai/grok-2-latest (xAI key varsa)
  5. groq/llama-3.1-8b-instant (groq key varsa)
  6. lmstudio/localhost:1234 (son care)
  7. Tumu basarisiz -> tools'suz metin cevap

### Neden:
- Hermes'te fallback chain var (deepseek->openrouter->...)
- ReYMeN'de _direct_api_call sadece DeepSeek API'sini cagiriyordu
- Beyin.uret_v2() zaten fallback destekliyordu ama config'de providers yoktu

## Karar #41: Takilma Korumasi (Hermes-style)
**Tarih:** 2026-07-05
**Ne yapildi:** duplicate detection + context budget + max_tool_calls eklendi

### Degisiklikler (src/reymen/cereyan/conversation_loop.py):
1. Sabitler: MAX_TOOL_CALLS=25, CONTEXT_BUDGET_CHARS=300000
2. __init__: _tool_call_sayaci, _onceki_tool_cagrilari, _context_budget_chars
3. Loop reset: her run_conversation basinda sayac sifirlama
4. max_tool_calls: tool_calls oncesi sayac kontrolu, asilirsa zorla cevap
5. Duplicate detection: ayni tool+parametre tekrari -> skip + "[DUPLICATE]" uyarisi
6. Context budget: _direct_api_call icinde mesaj boyutu kontrolu, eski mesajlardan trim

### Hermes'teki karsiligi:
- max_tool_calls=25 -> Hermes max_tool_calls=25 ile ayni
- Duplicate detection -> Hermes ayni tool+parametre tespiti
- Context budget -> Hermes ~80K token soft limit

### Etki:
- 25 tool call limiti -> sonsuz loop korumasi
- Ayni tool tekrari -> skip edilir, context sismez
- 300K char limit -> context overflow onlenir

## Karar #38 — conversation_loop.py: 3 kritik bulgu tespit edildi

**Tarih:** 2026-07-05
**Ne:** conversation_loop.py analizi sonucu 3 bug tespit edildi
**Neden:** Kullanıcı paste analizi gönderdi, ben fiilen test ettim

### Bulgu 1 — Kimlik Çelişkisi (BUG)
- **Dosya:** src/reymen/cereyan/conversation_loop.py satır 2571-2579
- **Sorun:** KIMLIK_SABITI bloğu 3 çelişkili ifade içeriyor: "Sen ReYMeN Agent'sin" + "Kesinlikle ReYMeN Agent degilsin" + "Ben ReYMeN Agent'im"
- **Kanıt:** DeepSeek API testi — çelişkili prompt boş yanıt döndürür
- **Tip:** BUG (çalışan kodu bozar)

### Bulgu 2 — Loop Break (BUG)
- **Dosya:** src/reymen/cereyan/conversation_loop.py satır 1462
- **Sorun:** `elif yanit_icerik:` bloğu model NE döndürürse döndürsün (soru/cevap fark etmez) koşulsuz break
- **Kanıt:** Kod okuması — soru/sonuç ayrımı yok
- **Tip:** BUG (model soru sorarsa loop biter)
- **Çözüm önerisi:** `_otonom_mod` flag + soru tespiti + continue (kullanıcı paste'inden)

### Bulgu 3 — Prompt Sızıntısı (BUG/ENHANCEMENT)
- **Kaynak:** Çelişkili identity + DeepSeek empty response fallback chain
- **Sorun:** "Bugun 05 July 2026. Sen ReYMeN adinda..." metni hiçbir dosyada yok; DeepSeek modeli çelişkili prompt karşısında boş döner, fallback'te prompt parçaları sızabilir
- **Kanıt:** 4 API testi — çelişkili prompt boş, temiz prompt düzgün çalışır
- **Tip:** BUG (kullanıcıya hatalı içerik gider)

### Alternatif düşünüldü mü?
Evet. Önce mevcut kodu okudum, sonra kullanıcının paste analizini doğruladım, sonra DeepSeek API ile 4 test çağrısı yaparak fiilen kanıtladım.

## Karar #41: Reasoning Asamasi Eklendi
- **Tarih:** 2026-07-05
- **Ne yapildi:** conversation_loop.py'ye "Asama 0: Reasoning" eklendi
- **Neden:** Kullanici soru akisinda once reasoning yap, sonra cevapla istedi
- **Nasil:** akilli_yonlendirici.py'deki gorevi_siniflandir() OnceHafiza'dan ONCE cagriliyor. Kategoriye gore prompt'a [REASONING] yonlendirmesi + AJAN_PERSONALARI talimati ekleniyor.
- **Dosyalar:** src/reymen/cereyan/conversation_loop.py
- **Yeni akis:** Reasoning(0) -> OnceHafiza(1) -> ONCELIK_CACHE(2) -> Web(3) -> LLM(4)
