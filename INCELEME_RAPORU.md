# ReYMeN-Ajan Derinlemesine İnceleme Raporu
**Tarih**: 2026-07-04 | **Versiyon**: v2026.07.04 | **Yazar**: MiMo Code Agent

---

## Proje Genel Bakış

| Metrik | Değer |
|--------|-------|
| **Toplam Python Dosyası** | 694 |
| **Toplam Kod Satırı** | 231,000+ |
| **Python Sürümü** | >= 3.11 |
| **Lisans** | MIT |
| **Giriş Noktası** | `reymen_launcher.py` (1058 satır) |
| **Paket Adı** | `reymen-agent` |
| **Build Sistemi** | Hatchling |

ReYMeN, Hermes Agent'tan fork'lanmış, kendi başına bağımsız çalışan, öz-düzeltmeli (self-healing), çok botlu otonom bir AI agent framework'üdür. 3 Telegram botunu tek merkezden yönetir, 17+ mesajlaşma platformuna bağlanır ve kapalı döngü öğrenme (closed-loop learning) özelliklidir.

---

## 1. Çekirdek Mimari (cereyan/) — 75 Dosya, 16,304 Satır

**Beyin → Motor → ConversationLoop** pipeline'ı:

### motor.py (3,141 satır) — Eylem Çözümleyici
- LLM çıktısından `Eylem: TOOL("param")` kalıbını regex ile ayrıştırır
- ~200 modülü otomatik yükler, ToolRegistry üzerinden yönlendirme yapar
- HITL (Human-in-the-Loop) onayı: KOMUT_CALISTIR, PYTHON_CALISTIR, TARAYICI_AC gibi riskli araçlar
- OpenAI function calling desteği (`calistir_fc`)

### beyin.py (1,603 satır) — LLM Üretim Katmanı
- **15+ sağlayıcı**: DeepSeek, OpenAI, Anthropic, Groq, Azure, AWS Bedrock, Gemini, Moonshot, Ollama, OpenRouter, Together, Fireworks, Mistral, Cohere, Perplexity
- Otomatik fallback zinciri: Birincil sağlayıcı hata verdiğinde diğerine geçiş
- Kesintili API çağrısı: Arka plan thread'inde çalıştırma, iptal desteği
- Streaming desteği (OpenAI SSE + Anthropic content_block_delta)

### conversation_loop.py (3,812 satır) — Ana Konuşma Döngüsü
- 4 fazlı ReAct döngüsü: SETUP → BUILD → REACT → POST-PROCESS
- Bağlam sıkıştırma: Token bütçesinin %75'i aşıldığında otomatik sıkıştırma
- Devre kesici: 3 ardışık hatada tüm API çağrısı durur
- Takılma algılama: Aynı eylem 3 kez tekrarlanırsa durur
- Hızlı yanıt önbelleği: "merhaba" → sıfır LLM maliyeti

### Diğer Önemli Modüller
| Dosya | Satır | Görev |
|-------|-------|-------|
| `steering_loop.py` | 741 | 5 katmanlı yönlendirme (SQLite + FTS5) |
| `alt_ajan.py` | 821 | Alt-ajan yönetimi (18 araç izni, döngü algılama) |
| `ajan_suru.py` | 286 | Çoklu agent tartışması (4 uzman rolü) |
| `planlayici.py` | 233 | Tree-of-Thought planlama |
| `hata_cozucu.py` | 627 | Hata izleme + OCR + düzeltme |
| `hata_siniflandirici.py` | 1,058 | 22 hata türü, 8 öncelik seviyesi |
| `closed_learning_loop.py` | 1,051 | FTS5 yetenek kristalleştirme + öz-iyileştirme |
| `hook_dispatcher.py` | 189 | 8 yaşam döngüsü olayı |
| `skill_library.py` | 681 | SQLite yetenek veritabanı |
| `provider_abstraction.py` | 749 | 5 somut sağlayıcı soyutlama |

---

## 2. Araç Sistemi (arac/) — 28 Dosya, 11,500+ Satır

**35+ motor-registered araç**:

| Kategori | Araçlar | Ana Dosyalar |
|----------|---------|--------------|
| **Dosya** | PDF, Excel, CSV okuma, dosya analizi | `araclar_dosya_analiz.py` (315) |
| **Ekran** | OCR okuma, tıklama | `araclar_ekran.py` (212) |
| **Tarayıcı** | Playwright MCP, Browser Use AI | `browser_engine.py` (379) |
| **Web** | 7 arama motoru (DDG, Firecrawl, Brave, Exa, SearXNG...) | `web_search_engine.py` (937) |
| **Video** | Bilgi çıkarma, Whisper transkripsiyon, video üretme | `araclar_video.py` (342), `video_gen_engine.py` (406) |
| **Ses** | Dinleme, tanıma, seslendirme (edge-tts, OpenAI TTS/STT) | `araclar_ses.py` (421), `voice_engine.py` (754) |
| **Görsel** | FAL, OpenAI DALL-E 3, xAI Grok üretim | `image_gen_engine.py` (580) |
| **Telegram** | Mesaj gönderme/okuma, dosya gönderme | `araclar_telegram.py` (451) |
| **CUA** | Bilgisayar Kullanım Ajanı (otomatik ekran etkileşimi) | `cua_motor_araci.py` (821) |
| **MCP** | stdio + HTTP MCP istemcileri, 9 hazır sunucu | `mcp_tool.py` (186), `mcp_client_tool.py` (502) |
| **Framework** | LangGraph, CrewAI, AutoGen adaptörleri | `framework_adaptor.py` (602) |
| **Makro** | Fare/klavye kaydı ve oynatma | `araclar_makro.py` (143) |
| **Toplu** | Thread havuzu tabanlı toplu işlem | `batch_engine.py` (423) |
| **Prompt** | Prompt oluşturma ve önbellek | `prompt_builder.py` (522), `prompt_caching.py` (238) |

**Tasarım Deseni**: Her araç modülü `motor_kaydet(motor)` fonksiyonu ile Motor'a kayıt olur. ABC + Registry deseni (web arama, ses, görsel üretim) ortak bir arayüz sağlar.

---

## 3. Hafıza Sistemi (hafiza/) — 20 Dosya, 11,500 Satır

**6 katmanlı hafıza mimarisi**:

```
Katman 6: SOUL.md / MEMORY.md / USER.md (insan-okunur kişilik)
Katman 5: .ReYMeN/skills/ + .ReYMeN/memories/ (kristalleşmiş yetenekler)
Katman 4: SQLite FTS5 (metin indeksli, yapılandırılmış)
Katman 3: ChromaDB / Vektörel Hafıza (anlamsal benzerlik)
Katman 2: İn-Process Çalışma Hafızası (LRU + SemanticCache)
Katman 1: Çökme-Güvenli JSON Dosyaları
```

| Dosya | Satır | Görev |
|-------|-------|-------|
| `hafiza_genislet.py` | 1,432 | **En büyük** — SQLite FTS5, 4 koleksiyon, otomatik konsolidasyon |
| `session_db.py` | 1,227 | Oturum veritabanı, maliyet/token takibi, FTS5 arama |
| `gorev_once_kontrol.py` | 1,080 | 5 katmanlı görev öncesi hafıza kontrolü |
| `gorev_hafiza.py` | 939 | Görev sonrası konsolidasyon (4 hedefe yazma) |
| `memory_provider.py` | 1,170 | Plugin tabanlı arka plan soyutlama (JSON/SQLite/ChromaDB) |
| `vektor_bellek.py` | 505 | ChromaDB + SQLite yedekleme |
| `hafiza_budama.py` | 536 | TTL tabanlı budama + benzer kayıtları birleştirme |
| `context_manager.py` | 219 | LLM destekli_trajektori sıkıştırma |
| `bounded_memory.py` | 325 | LRU sınırlı hafıza |
| `semantic_cache.py` | 281 | LLM yanıt önbelleği |

**Önemli Desenler**: Güven skoru (`basari/(basari+hata)`), geçerlilik süresi (varsayılan +180 gün), her yerde çoğaltma engelleme.

---

## 4. Güvenlik Katmanı (guvenlik/) — 24 Dosya, 8,265 Satır

**7 katmanlı savunma derinliği**:

| Katman | Dosya(lar) | Görev |
|--------|-----------|-------|
| **1. Kimlik & Erişim** | `reymen_auth.py` (866), `auth_middleware.py` (325), `oauth2.py` (444), `oauth_sistemi.py` (876) | JWT (HMAC-SHA256, sıfır harici kripto), OAuth2 (Google, Discord, GitHub), FastAPI/Flask middleware |
| **2. Ağ Kısıtlama** | `network_restriction.py` (884) | Dış trafiği engelleme (netsh/iptables/hosts), Docker iç ağ |
| **3. Kod Çalıştırma Sandalboxı** | `guvenli_sandbox.py` (320), `container_sandbox.py` (622), `docker_sandbox.py` (503) | 3 kademeli: subprocess (modül izin listesi) → Docker partial → Docker full (read-only, 256MB) |
| **4. Araç Guardrail** | `tool_guardrails.py` (286) | 10 tehlikeli araç, parametre tarama, shell enjeksiyon algılama |
| **5. Girdi/Çıktı Temizleme** | `message_sanitization.py` (203), `threat_patterns.py` (97), `redact.py` (62) | HTML/ANSI temizleme, prompt injection algılama (11 kalıp), PII maskeleme (e-posta, telefon, kart, TC kimlik) |
| **6. Hallucination & Anayasa** | `guardrails.py` (309), `anayasa_denetci.py` (225) | 6 kontrollü halüsinasyon filtresi, 10 ilkeli Anayasa AI (LLM meta-değerlendirme) |
| **7. Dosya/Yol/URL** | `file_safety.py` (98), `path_security.py` (58), `url_safety.py` (86) | Yasaklı dizinler/uzantılar, sembolik link kontrolü, riskli TLD filtresi |

**Tasarım Kararları**: Sıfır harici güvenlik bağımlılığı (tüm kripto, PII tespiti, ağ kontrolleri stdlib kullanır). Her bağımlılık try/except ile sarılmış.

---

## 5. Sistem & CLI (sistem/) — 125+ Dosya

### CLI Mimarisi (13 Mixin)
`ReYMeNCLI` sınıfı 13 mixin'den türetilir:
- TUIMixin (prompt_toolkit TUI), AgentMixin (agent yaşam döngüsü), SessionMixin
- MixinDisplay, MixinStream, MixinVoice, MixinApproval, MixinCommands
- MixinCore, MixinFileOps, MixinMedia, MixinAgentSettings, MixinBrowser
- MixinGoals, MixinSkillsTools, MixinUI

**59 slash komutu**: /help, /clear, /model, /tools, /skills, /cron, /kanban, /voice, /browser, /agents, /goal, /compress, /rollback, /snapshot...

### Durum Makinesi (12 durum)
```
UNINITIALIZED → INITIALIZING → IDLE → THINKING → TOOL_CALL → WAITING
                                  ↓                ↓
                              ERROR → RECOVERING → DEGRADED
                                                          ↓
                                              SHUTDOWN | CRASHED
```

### Altyapı Modülleri
| Modül | Görev |
|-------|-------|
| `config_loader.py` (346) | YAML config yükleme, derinleştirme |
| `cron_scheduler.py` (448) | Cron ifadesi ayrıştırıcı + zamanlayıcı |
| `health_check.py` (552) | Disk/bellek/modül/API/sistem dosyası kontrolü |
| `plugin_loader.py` (375) | Plugin keşfi ve yüklemesi |
| `plugin_manager.py` (872) | Plugin yönetimi + marketplace |
| `circuit_breaker.py` (87) | 3 durumlu arıza toleransı |
| `auto_recovery.py` (554) | Watchdog + bileşen kurtarma |
| `rate_limiter.py` (278) | Kaydırma penceresi RPM + token bütçesi |
| `surekli_ogrenme.py` (226) | JSONL çapraz oturum öğrenme |

---

## 6. Gateway Sistemi (gateways/) — 71 Dosya, 48,000+ Satır

### Mesaj Akışı
```
Platform (Telegram/Discord/...)
    ↓
PlatformAdapter.connect() → MessageEvent
    ↓
GatewayRunner._handle_message()
    → Yetkilendirme (authz_mixin)
    → Slash komut yönlendirmesi
    → Oturum çözümleme (session.py + contextvars)
    → Agent çalıştırma (provider_router + circuit breaker)
    ↓
Agent yanıtı → DeliveryRouter → adapter.send()
    → Streaming (stream_consumer.py — yerinde düzenleme)
    ↓
Platform yanıtı
```

### 22+ Platform Adaptörü
| # | Platform | Satır | Özellikler |
|---|----------|-------|------------|
| 1 | **Telegram** | 6,962 | Forum konuları, DM konuları, inline klavyeler, streaming draft'lar |
| 2 | **WhatsApp** | 1,314 | Cloud API, webhook, HMAC-SHA256 doğrulama |
| 3 | **Discord** | 702 | Standalone bot (discord.py) |
| 4 | **Slack** | 361 | Events API + RTM, mesaj çoğaltma engelleme |
| 5 | **Teams** | 410 | Graph API, OAuth 2.0 |
| 6 | **Matrix** | 504 | Client-server REST API v1.12 |
| 7 | **Mattermost** | 557 | REST API v4 |
| 8 | **Signal** | 324 | signal-cli REST API |
| 9 | **Email** | 514 | SMTP/IMAP |
| 10 | **SMS** | 325 | Twilio |
| 11-22 | Home Assistant, WeCom, DingTalk, Feishu, BlueBubbles, QQ Bot, Yuanbao, Google Chat... | 200-440 arası | Her biri platform-spesifik API |

### Altyapı
- `base.py` (5,358 satır) — Tüm adaptörlerin soyut temel sınıfı
- `session.py` (1,354) — Oturum yönetimi, sıfırlama politikası
- `stream_consumer.py` (1,542) — Canlı düzenleme ile streaming
- `provider_router.py` (297) — Devre kesici + sağlık kontrolü
- `mcp_server.py` (595) — MCP protokolü sunucusu (JSON-RPC 2.0)
- `slash_commands.py` (3,876) — 42 slash komutu
- `config.py` (2,272) — 27 platform enum'u

---

## 7. Test Süiti — 1,907 Dosya, ~38,862 Test Fonksiyonu

| Metrik | Değer |
|--------|-------|
| **Test Framework** | pytest 9.1.0 + pytest-cov 7.1.0 |
| **Toplam test dosyası** | 1,907 |
| **Root-level test dosyası** | 230 |
| **Kabul edilen test** | 105 dosya (root seviyesinde) |
| **En büyük test dosyası** | `test_hafiza.py` (1,195 satır, 62 fonksiyon) |
| **Son başarılı kapsama** | 188K satırda %100 |
| **Son test çalıştırma** | BAŞARISIZ (1 test_core_imports hatası) |
| **Hariç tutulanlar** | ReYMeN_reference/ (1,513 dosya), hermes_legacy/ (49 dosya) |

**Test Desenleri**: Sınıf tabanlı (`class Test*`), pytest fixtures, `@pytest.mark.parametrize`, `unittest.mock.patch`, :memory: SQLite, async (`@pytest.mark.asyncio`).

---

## 8. Konfigürasyon & Bağımlılıklar

### Ana Config (config.yaml — 255 satır)
- **Birincil model**: `deepseek/deepseek-v4-flash`
- **Fallback zinciri**: 11 sağlayıcı (DeepSeek → Xiaomi MiMo → xAI Grok → OpenRouter → OpenAI → Anthropic → Groq → LM Studio → Reasoning-Core)
- **Sandbox**: Kısmi Docker (python:3.11-slim, 1GB RAM, 2 CPU)
- **Auth**: JWT (1 saat erişim, 24 saat yenileme)
- **MCP sunucuları**: filesystem + playwright
- **Bellek**: 10K char/oturum, 50K global, 2K kayıt

### Çevresel Değişkenler (.env.example — 91 satır)
- **Zorunlu**: Sadece `DEEPSEEK_API_KEY`
- **İsteğe bağlı**: 6 LLM anahtarı, 3 Telegram token, Discord, Slack, Teams, Home Assistant, Signal, Matrix, DingTalk, Feishu, WeCom, SSH, Daytona, JWT, Langfuse, Firecrawl, Brave, GitHub

### Core Bağımlılıklar (19 paket)
requests, pyyaml, python-dotenv, psutil, pillow, numpy, httpx, rich, prompt_toolkit, pydantic, openai, beautifulsoup4, duckduckgo_search, edge-tts, python-telegram-bot, fastapi, uvicorn + OpenTelemetry

---

## 9. Uygulamalar & Ekosistem

### Frontend Uygulamaları
- **Desktop**: Electron 40 + Vite 8 + React 19 + TypeScript (Mac/Win/Linux)
- **Bootstrap Installer**: Tauri 2 (Rust) + Vite + React (5-10MB imzalı)
- **Paylaşım**: JSON-RPC 2.0 WebSocket protokolü

### Plugin Ekosistemi (21 plugin, 143+ dosya)
| Plugin | İçerik |
|--------|--------|
| **memory/** | 8 hafıza sağlayıcısı (mem0, honcho, holographic, hindsight...) |
| **browser/** | 3 tarayıcı (Browser Use, Browserbase, Firecrawl) |
| **model-providers/** | **29 LLM sağlayıcı** (Alibaba, Anthropic, Azure, Bedrock, DeepSeek, Gemini, Groq, OpenAI, xAI, Xiaomi...) |
| **platforms/** | 11 mesajlaşma platformu (Discord, Google Chat, IRC, LINE, Mattermost...) |
| **observability/** | Langfuse, NeMo Relay |
| **image_gen/** | Fal, Krea, OpenAI, xAI |
| **video_gen/** | Fal, xAI |
| **web/** | 8 arama motoru (Brave, DDG, Exa, Firecrawl, Tavily...) |
| **spotify/** | 7 araç (oynatma, cihazlar, kuyruk, arama...) |
| **security-guidance/** | 25 güvenlik kuralı |

### Yetenek Kütüphanesi (531 Markdown dosyası)
ML/AI, güvenlik, mimari, prompt mühendisliği, MCP, platform-spesifik, Türkçe.

### Yerelleştirme (16 dil)
af, de, en, es, fr, ga, hu, it, ja, ko, pt, ru, tr, uk, zh, zh-hant

---

## Kritik Bulgular & Öneriler

### Güçlü Yönler
1. **Olağanüstü kapsamlı** — 231K+ satır, 17+ platform, 29 LLM sağlayıcı
2. **Derinlemesine güvenlik** — 7 katmanlı savunma, sıfır harici kripto bağımlılığı
3. **Öğrenen sistem** — Kapalı döngü öğrenme, FTS5 yetenek kristalleştirme
4. **Graceful degrade** — Her bağımlılık optional, her hata yolu ele alınmış
5. **Zengin ekosistem** — Electron/Tauri frontend, 531 skill, 16 dil

### İyileştirme Alanları
1. **Test kararlılığı** — Son test çalıştırması başarısız, coverage runner 0.7sn'de bitiyor
2. **Eski kod kalıntıları** — `ReYMeN_cli/` (175 dosya) ile yeni CLI arasında çakışma riski
3. **Motor.py boyutu** — 3,141 satır, ~200 modül yüklemesi. Modülerleştirme önerilir
4. **Dual plugin sistemi** — PluginYukleyici + PluginManager birleştirilebilir
5. **Dokümantasyon** — Türkçe/İngilizce karışık, API dokümantasyonu eksik

### Mimari Kararlar
1. **Bağımsızlık**: Hermes'ten fork edilmiş ama sıfır Hermes bağımlılığı beyan edilmiş
2. **Türkçe isimlendirme**: Tüm API'ler, değişkenler, hata mesajları Türkçe (calistir, kaydet, hata...)
3. **SQLite evrensel depolama**: FTS5, WAL modu, tetikleyiciler ile her yerde
4. **Thread over asyncio**: "LLM çağrıları I/O bound, threading yeterli" felsefesi
5. **Çoklu devre kesici**: conversation_loop, steering_loop, alt_ajan, provider_router seviyelerinde

---

*Bu rapor 9 aşamalı paralel inceleme sonucu oluşturulmuştur. Her modül detaylıca okunarak mimari kararlar, bağımlılıklar ve potansiyel sorunlar belirlenmiştir.*
