# 📖 ReYMeN API Referansı

> Sürüm: 0.9.0 · Python 3.11+

---

## 📦 Ana Modüller

### reymen (kök paket)

`reymen/__init__.py`

```
__version__ = "0.9.0"
```

**Alt modüller:** `cost_tracker`, `platform_adapter`, `tui`, `self_improve`, `kanban`, `video_tools`, `a2a`

---

## 🤝 A2A Mesajlaşma — `reymen.a2a`

Agent'lar arası thread-safe kuyruk tabanlı mesajlaşma protokolü.

### Sınıflar

#### `MessageType(str, Enum)`
Mesaj tipleri: `TEXT`, `TASK`, `RESULT`, `QUERY`, `RESPONSE`, `ERROR`, `BROADCAST`, `HEARTBEAT`

#### `Message(sender, receiver, content, type=TEXT, id=uuid, reply_to=None, timestamp, metadata={})`
A2A mesaj veri yapısı.

| Metod | Dönüş | Açıklama |
|-------|-------|----------|
| `as_dict()` | `dict` | Mesajı sözlüğe çevir |
| `reply(content, msg_type=None)` | `Message` | Yanıt mesajı oluştur (sender↔receiver ters çevrilir) |

#### `Broker()`
Merkezi mesaj broker'ı. Thread-safe.

| Metod | Dönüş | Açıklama |
|-------|-------|----------|
| `register(agent_id)` | `None` | Agent kaydet |
| `unregister(agent_id)` | `None` | Agent kaydını sil |
| `is_registered(agent_id)` | `bool` | Kayıtlı mı? |
| `send(message)` | `None` | Mesaj gönder (hedef kayıtlı değilse `A2AError`) |
| `broadcast(sender, content, exclude=None)` | `list[str]` | Tüm agent'lara yayın |
| `receive(agent_id, timeout=None, block=True)` | `Message\|None` | Mesaj al |
| `peek(agent_id)` | `Message\|None` | Silmeden oku |
| `inbox_size(agent_id)` | `int` | Bekleyen mesaj sayısı |
| `set_handler(agent_id, handler)` | `None` | Mesaj handler'ı ayarla |
| `clear_handler(agent_id)` | `None` | Handler'ı temizle |
| `message_log()` | `list[Message]` | Tüm iletilen mesajlar |
| `stats()` | `dict` | Broker istatistikleri |
| `reset()` | `None` | Tüm inbox'ları ve log'u temizle |

#### `Agent(agent_id, broker, on_message=None)`
A2A agent'ı. Oluşturulurken otomatik broker'a kaydolur.

| Metod | Dönüş | Açıklama |
|-------|-------|----------|
| `send(receiver, content, msg_type=TEXT, reply_to=None, metadata=None)` | `Message` | Mesaj gönder |
| `broadcast(content, exclude=None)` | `list[str]` | Tüm agent'lara yayın |
| `reply(original, content)` | `Message` | Yanıt ver |
| `receive(timeout=None, block=True)` | `Message\|None` | Mesaj al |
| `peek()` | `Message\|None` | Silmeden oku |
| `inbox_size` | `int` (property) | Bekleyen mesaj sayısı |
| `set_handler(handler)` | `None` | Mesaj handler'ı ayarla |
| `clear_handler()` | `None` | Handler'ı temizle |
| `close()` | `None` | Broker'dan kaydı sil |

### Hata Sınıfı

**`A2AError(RuntimeError)`** — A2A mesajlaşma hatası (örn. hedef agent kayıtlı değil)

---

## 🛠️ Araç Katmanı — `reymen.arac`

### BrowserTool — `araclar_gelismis.py`

Headless Chromium (Playwright) + urllib fallback.

| Metod | Açıklama |
|-------|----------|
| `ac(url)` | Sayfa aç, metin oku |
| `screenshot(url="", cikti="screenshot.png")` | Ekran görüntüsü al |
| `js_calistir(url="", js="document.title")` | JavaScript çalıştır |
| `tikla(secici)` | Elemente tıkla |
| `fill(secici, deger)` | Form alanı doldur |
| `type_text(secici, deger)` | Karakter karakter yaz |
| `select_option(secici, deger)` | Dropdown seç |
| `wait_for(secici, timeout=10)` | Element bekle |
| `wait_for_text(metin, timeout=10)` | Metin bekle |
| `hover(secici)` | Üzerine gel |
| `scroll(dx=0, dy=300)` | Sayfayı kaydır |
| `scroll_to(secici)` | Elemente kaydır |
| `back()` / `forward()` / `reload()` | Geçmiş yönetimi |
| `new_tab(url="")` | Yeni sekme aç |
| `switch_tab(index)` | Sekmeye geç |
| `close_tab(index=-1)` | Sekme kapat |
| `tabs_list()` | Açık sekmeleri listele |
| `snapshot(maks=3000)` | Sayfa metnini döndür |
| `html(maks=3000)` | Sayfa HTML'ini döndür |
| `title()` / `url()` | Başlık / URL |
| `dialog_accept()` / `dialog_dismiss()` | Dialog yönetimi |
| `network_requests(limit=10)` | Network isteklerini izle |
| `cookies()` / `clear_state()` | Cookie/state yönetimi |
| `kapat()` | Tarayıcıyı kapat |

### TarayiciKontrol — `araclar_tarayici.py`

Basit, her işlemde yeni tarayıcı açar/kapatır.

| Metod | Açıklama |
|-------|----------|
| `sayfa_ac_ve_oku(url, secici=None)` | URL aç, metin döndür |
| `tikla_ve_yaz(url, tiklanacak_secici, yazi_secici, yazi)` | Tıkla + yaz |

---

## 🧠 LLM Katmanı — `reymen.cereyan.beyin`

**`Beyin`** — Çok-sağlayıcılı LLM bağlantı katmanı. 12+ provider, otomatik failover.

| Metod | Açıklama |
|-------|----------|
| `dusun(mesajlar, tools=None, stream=False)` | LLM sorgula |
| `iptal_et()` | Mevcut isteği iptal et |
| `sifirla()` | Rate-limit state'ini sıfırla |
| `dusun_stream(mesajlar, tools=None)` | Streaming sorgu |

**Desteklenen Provider'lar:** LM Studio, DeepSeek, OpenAI, Anthropic, Groq, Azure, Bedrock, Gemini, Moonshot, Ollama, OpenRouter, xAI

---

## 🔄 Konuşma Döngüsü — `reymen.cereyan.conversation_loop`

### `GorevCozucu(motor=None, beyin=None, max_tur=30)`

7 kaynaklı ensemble karşılaştırma ile akıllı görev çözümü.

| Metod | Açıklama |
|-------|----------|
| `coz(hedef, baglam=None)` | Basit API (eski) |
| `run_conversation(hedef, baglam=None, provider=None)` | Gelişmiş API (Hermes pipeline) |

**Akış:** SORGU → OnceHafıza → Session search → Skill tarama → Ensemble (7 kaynak) → Kaydet → Cevap

---

## 🎯 Eylem Motoru — `reymen.cereyan.motor`

### `Motor(backend_mode="local", hafiza_collection=None, config=None)`

LLM çıktısından eylem yakalar, ToolRegistry + plugin'ler üzerinden yönlendirir.

| Metod | Açıklama |
|-------|----------|
| `hook_kaydet(olay, fn)` | Motor hook'u kaydet |
| `calistir(arac, ham_param)` | Araç çalıştır |
| `calistir_fc(arac, args)` | Function-calling formatında çalıştır |
| `tools_schema_al(maks=64)` | OpenAI-uyumlu tool schema üret |
| `tum_arac_tanimini_al()` | Tüm araç tanımlarını döndür |
| `gorev_coz(gorev_yolu)` | Görev dosyasını çöz |
| `eylemi_ayristir(llm_cikti)` | LLM çıktısından eylem adı+param ayıkla |
| `musait_araclar(toolset=None)` | Kullanılabilir araçları listele |

---

## 🧩 Hook Sistemi — `reymen.cereyan.hook_dispatcher`

8 olay tipi için fonksiyon tabanlı hook sistemi.

### Olay Tipleri

| Olay | Tetikleyici | Ne Zaman |
|------|-------------|----------|
| `on_session_start` | `oturum_baslat_tetikle()` | Oturum başlarken |
| `on_session_end` | `oturum_bitir_tetikle()` | Oturum biterken |
| `on_turn_start` | `tur_baslat_tetikle()` | Her tur başında |
| `on_turn_end` | `tur_bitir_tetikle()` | Her tur sonunda |
| `on_tool_call` | `arac_cagri_tetikle()` | Araç çağrılmadan önce |
| `on_tool_result` | `arac_sonuc_tetikle()` | Araç sonucu alındıktan sonra |
| `on_error` | `hata_tetikle()` | Hata oluştuğunda |
| `on_context_compress` | `context_sikistirma_tetikle()` | Context sıkıştırılmadan önce |

### Fonksiyonlar

| Fonksiyon | Açıklama |
|-----------|----------|
| `hook_kaydet(olay, callback)` | Hook callback kaydet |
| `hook_kaldir(olay, callback)` | Hook kaldır (bool döner) |
| `hook_cagir(olay, **kwargs)` | Tüm callback'leri ateşle |
| `hook(olay)` | Decorator: `@hook("on_session_start")` |
| `kayitli_hooklar()` | Kayıtlı hook'ların özeti |
| `tum_hooklari_temizle()` | Tümünü temizle (test izolasyonu) |

---

## 💬 Mesaj Broker — `reymen.cereyan.broker`

### `MessageBroker`
queue.Queue tabanlı, thread-safe, 18 mesaj tipi.

| Metod | Açıklama |
|-------|----------|
| `abone_ol(consumer_id, mesaj_tipleri, callback)` | Mesaj tipine abone ol |
| `abone_ol_liste(consumer_id, mesaj_tipleri, callback)` | Liste ile abone ol |
| `yayinla(mesaj)` | Mesaj yayınla |
| `yayinla_basit(tip, veri, kaynak="")` | Basit yayın |
| `baslat()` | Broker'ı başlat |
| `durdur()` | Broker'ı durdur |
| `durum()` | Durum raporu |

**18 Mesaj Tipi:** HATA, COZUM_ARA, COZUM_BULUNDU, GOREV_VER, GOREV_ALINDI, GOREV_TAMAM, GOREV_IPTAL, TOOL_CALL, TOOL_SONUC, BILGI, UYARI, DURDUR, DEVRAL, YAYIN, SES, GORUNTU, LOG, KONTROL

---

## 💰 Cost Tracking — `reymen.cost_tracker`

SQLite tabanlı API harcama takibi.

### `CostTracker`

| Metod | Açıklama |
|-------|----------|
| `compute_cost(model, input_tokens, output_tokens)` | Maliyet hesapla |
| `record(model, input_tokens, output_tokens, cost, provider="", metadata=None)` | Kayıt ekle |
| `summary()` | Özet rapor |
| `dump_log(limit=50)` | Son kayıtlar |
| `reset()` | Tüm kayıtları sil |
| `iter_records()` | Tüm kayıtlar üzerinde iterasyon |

### Modül Fonksiyonları

`record_usage()`, `summary()`, `dump_log()`, `reset()`, `set_db_path()`, `set_price_table()`

---

## 📊 Kanban — `reymen.kanban`

### `Board`

WIP limitli, öncelik sıralamalı, deadline destekli kanban panosu.

| Metod | Açıklama |
|-------|----------|
| `add(kart, kolon="backlog")` | Kart ekle |
| `move(kart_id, hedef_kolon)` | Kart taşı |
| `set_status(kart_id, durum)` | Durum güncelle |
| `prioritize(kart_id, oncelik)` | Öncelik değiştir |
| `find(kart_id)` | Kart bul |
| `complete(kart_id)` | Tamamlandı olarak işaretle |
| `summary()` | Pano özeti |
| `save()` / `load()` | Kalıcı depolama |
| `to_json()` / `from_dict()` | Serileştirme |

### Worker API

`kanban_create()`, `kanban_show()`, `kanban_complete()`, `kanban_block()`, `kanban_unblock()`, `kanban_comment()`, `kanban_heartbeat()`, `kanban_claim()`, `kanban_list()`, `kanban_summary()`, `kanban_delete_card()`

---

## 🌍 Platform Adapter — `reymen.platform_adapter`

### `PlatformAdapter` (temel sınıf)

| Metod | Açıklama |
|-------|----------|
| `info()` | Platform bilgisi |
| `translate_path(yol)` | Yol çevir (örn. C:\ → /mnt/c/) |
| `run(komut)` | Komut çalıştır |

**Alt sınıflar:** `NativeAdapter`, `WSLAdapter`, `KaliAdapter`

### Modül Fonksiyonları

`detect()` — Platform algıla, `translate_path()`, `run()`, `is_wsl_available()`, `list_wsl_distros()`

---

## 🔄 Self-Improvement — `reymen.self_improve`

### `SelfImprover`

Kalite metrikleri, trend analizi ve otomatik iyileştirme.

| Metod | Açıklama |
|-------|----------|
| `record(metric)` | Metrik kaydet |
| `history()` | Geçmiş metrikler |
| `trend()` | Trend analizi |
| `low_quality_steps(threshold=0.5)` | Düşük kaliteli adımlar |
| `auto_improve()` | Otomatik iyileştirme önerisi |
| `reset()` | Sıfırla |

### Modül Fonksiyonları

`evaluate()`, `suggest_fix()`, `record_step()`, `record_step_with_cost()`, `report()`, `reset_history()`

---

## 🪟 TUI — `reymen.tui`

Rich tabanlı terminal arayüzü.

| Fonksiyon | Açıklama |
|-----------|----------|
| `with_spinner(metin)` | Spinner context manager |
| `progress_bar(iterable, aciklama="")` | Progress bar |
| `info()` / `success()` / `warning()` / `error()` | Renkli mesajlar |
| `panel(icerik, baslik="")` | Rich panel |
| `table(sutunlar, satirlar)` | Rich tablo |

### `StatusBar`
Tek satırlık durum çubuğu.

---

## 🎬 Video Araçları — `reymen.video_tools`

yt-dlp + ffmpeg wrapper.

| Fonksiyon | Açıklama |
|-----------|----------|
| `download(url, format="best")` | Video indir |
| `probe(path)` | Video bilgisi |
| `convert(kaynak, hedef)` | Format dönüştür |
| `extract_audio(kaynak, hedef)` | Ses çıkar |
| `cut(kaynak, baslangic, bitis, hedef)` | Video kes |

### Sınıflar

`VideoInfo` — İndirilen video bilgisi (dataclass)
`FFmpegResult` — ffmpeg sonucu (dataclass)

---

## 🌐 Web UI — `reymen.web_ui`

FastAPI + HTMX yönetim paneli.

| Route | Açıklama |
|-------|----------|
| `/` | Ana sayfa |
| `/api/durum` | Sistem durumu |
| `/api/gateway/restart` | Gateway yeniden başlat |
| `/api/loglar` | Sistem logları |
| `/api/bot/test` | Bot test |

---

## 🧠 Core Modüller

### Model Adapter — `reymen.core.model_adapter`

| Sınıf | Açıklama |
|-------|----------|
| `ModelAdapter` (protocol) | `complete(prompt) -> str` |
| `OllamaAdapter` | localhost:11434 |
| `OpenAICompatAdapter` | LM Studio / DeepSeek / OpenAI |
| `AnthropicAdapter` | Claude API |

`get_active_adapter()` — REYMEN_MODEL env ile adapter seçimi.

### Orchestrator — `reymen.core.orchestrator`

| Fonksiyon | Açıklama |
|-----------|----------|
| `run_script(path)` | Python script çalıştır |
| `solve_step(step_name, script_path)` | Tek adım çöz (max 3 retry) |
| `solve_all(steps)` | Tüm adımları sırayla çöz |
| `coz_hata(hata, kod, ad)` | Hata LLM'e sor |

### Öğrenme — `reymen.core.ogrenme`

Hata→çözüm hafızası (SQLite, TTL=30 gün).

| Fonksiyon | Açıklama |
|-----------|----------|
| `imza_uret(hata)` | Hata imzası oluştur |
| `cozum_bul(imza)` | Kayıtlı çözüm ara |
| `cozum_kaydet(imza, hata_tipi, hata_ozet, cozum_kodu)` | Çözüm kaydet |
| `tablo_olustur()` | DB tablolarını oluştur |
| `istatistik()` | Öğrenme istatistikleri |
| `ttl_temizle()` | Eski kayıtları temizle |

### Session Search — `reymen.core.session_search`

FTS5 tabanlı geçmiş konuşma arama.

| Fonksiyon | Açıklama |
|-----------|----------|
| `session_ara(sorgu, limit=5)` | FTS5 arama |
| `session_listele(limit=10)` | Son session'lar |
| `session_mesajlari(session_id)` | Session mesajları |
| `session_istatistik()` | İstatistikler |

### MCP Server — `reymen.core.mcp_server`

Model Context Protocol sunucusu.

| Fonksiyon | Açıklama |
|-----------|----------|
| `tool_kaydet(ad, fonk, aciklama, schema)` | Tool kaydet |
| `tool_sil(ad)` | Tool sil |
| `get_tools()` | Tüm tool'lar |
| `resource_kaydet(uri, okuyucu)` | Resource kaydet |
| `prompt_kaydet(ad, olusturucu)` | Prompt kaydet |

**Varsayılan Tool'lar:** ReYMeN_status, memory_search, session_search, file_read, file_write, shell

---

## 🔐 Güvenlik — `reymen.guvenlik`

| Modül | Açıklama |
|-------|----------|
| `file_safety.py` | `guvenli_mi(yol)` — dosya güvenlik kontrolü |
| `path_security.py` | `yol_dogrula(yol)` — path doğrulama |
| `redact.py` | `tam_temizle(mesaj)` — PII redaction |
| `guardrails.py` | Çıktı guardrail'leri |
| `guvenli_sandbox.py` | `guvenli_calistir(kod)` — izole Python çalıştırma |
| `security_engine.py` | Tehdit algılama motoru |
| `anayasa_denetci.py` | Anayasal AI denetimi |

---

## 🧠 Hafıza — `reymen.hafiza`

| Modül | Açıklama |
|-------|----------|
| `once_hafiza.py` | Vektör tabanlı öncelikli hafıza |
| `session_db.py` | FTS5 session veritabanı |
| `context_compressor.py` | Bağlam sıkıştırma |
| `memory_manager.py` | Hafıza yöneticisi |
| `bounded_memory.py` | Sınırlandırılmış bellek |
| `gorev_hafiza.py` | Görev geçmişi |
| `vektorel_hafiza.py` | Vektör hafıza (ChromaDB) |

---

## 🪟 Windows — `reymen.windows`

| Modül | Açıklama |
|-------|----------|
| `windows_entegrasyon.py` | Windows sistem entegrasyonu |
| `trajectory.py` | Windows olay takibi |
| `trajectory_compressor.py` | Trajectory sıkıştırma |
| `tor_otomasyonu.py` | Tor tarayıcı otomasyonu |
| `browser_camofox.py` | Firefox tabanlı browser |
| `otonom_nisan_olusturucu.py` | Otonom hedef oluşturucu |
| `screenshot_bot.py` | Ekran görüntüsü botu |
| `nisan_yakala.py` | Hedef yakalama aracı |

---

## ⚙️ CLI — `reymen.sistem`

| Modül | Açıklama |
|-------|----------|
| `cli_main.py` | Ana CLI (4.857 satır) |
| `cli_agent.py` | Agent lifecycle (2.618 satır) |
| `cli_session.py` | Session yönetimi |
| `cli_display.py` | Görüntüleme mixin |
| `cli_stream.py` | Streaming mixin |
| `cli_commands.py` | Komut yönetimi |
| `run_agent.py` | Agent çalıştırıcı (4.858 satır) |
| `main.py` | AIAgentOrchestrator (1.582 satır) |
| `motor.py` | Eylem motoru (1.950 satır) |

---

## 🧩 Alt CLI'lar

| Komut | Açıklama |
|-------|----------|
| `reymen status` | Sistem durumu |
| `reymen cost` | Maliyet görüntüle |
| `reymen platform` | Platform bilgisi |
| `reymen quality` | Kalite raporu |
| `reymen kanban` | Kanban yönetimi |
| `reymen video` | Video işlemleri |
| `reymen a2a` | A2A test |
| `reymen web` | Web UI başlat |
| `reymen backup` | Yedekleme |
| `reymen cron` | Cron job yönetimi |
| `reymen config` | Yapılandırma |
| `reymen debug` | Debug araçları |
| `reymen doctor` | Sistem tanılama |
