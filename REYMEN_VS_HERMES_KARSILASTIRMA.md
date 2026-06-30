# ReYMeN Agent vs Hermes Agent — Güncel Karşılaştırma

**Tarih:** 2026-06-29 (Güncellendi)
**Önceki Rapora Göre Fark:** 6 yeni özellik tamamlandı (Provider, Profile, Gateway Multi, Vector Memory, OAuth 2.0, Delegation)

---

## 1. GÜNCEL DURUM TABLOSU (29 Özellik)

| # | Özellik | Eski Durum | YENİ Durum | Detay |
|---|---------|-----------|-----------|-------|
| 1 | **Provider Sistemi** | ❌ Eksik | ✅ **TAM** | Model routing (33 mapping) + failover chain + circuit breaker |
| 2 | **YAML Config/Profile** | ❌ Eksik | ✅ **TAM** | 4 profil (reymen/dev/test/prod) + override mekanizması |
| 3 | **Session DB (FTS5)** | ❌ Eksik | ✅ **TAM** | FTS5 + trigram arama, SQLite session storage |
| 4 | **Cron/Scheduler** | ❌ Eksik | ✅ **TAM** | Per-job override, watchdog, per-job model override |
| 5 | **Gateway Sistemi** | ⚠️ Kısmi | ✅ **TAM** | ABC GatewayBase + 4 platform (TG/CLI/Web/DC) + GatewayManager |
| 6 | **Vector Memory** | ❌ Eksik | ✅ **TAM** | ChromaDB embedding + semantic search + SQLite fallback |
| 7 | **OAuth 2.0** | ❌ Eksik | ✅ **TAM** | Google/GitHub/Discord + SQLite token deposu + FastAPI callback |
| 8 | **Delegation** | ❌ Eksik | ✅ **TAM** | Subagent TEK/PARALEL/ZİNCİR mod + izole context |
| 9 | **Backup Sistemi** | ❌ Eksik | ✅ **TAM** | ZIP yedekleme, CLI create/restore |
| 10 | **Guardrails** | ❌ Eksik | ✅ **TAM** | Threat patterns + PII detection + tool guardrails |
| 11 | **MCP Client** | ⚠️ Kısmi | ✅ **TAM** | Runtime auto-discovery + reconnect test |
| 12 | **Plugin Sistemi** | ⚠️ Kısmi | ⚠️ **Kısmi** | Hot-reload yok, provider plugin kavramı yok |
| 13 | **Skills** | ⚠️ Kısmi | ✅ **TAM** | Auto-activation + cron sync + context injection |
| 14 | **Web Search** | ⚠️ Kısmi | ✅ **TAM** | ABC 7 engine (DDG/Firecrawl/Brave/SearXNG/Exa/Google/Bing) |
| 15 | **Image Generation** | ⚠️ Kısmi | ❌ **Eksik** | FAL/OpenAI/xAI entegrasyonu yok |
| 16 | **Browser Automation** | ⚠️ Kısmi | ✅ **TAM** | Playwright MCP + Browser Use unified engine |
| 17 | **Security/Sandbox** | ⚠️ Kısmi | ✅ **TAM** | Docker sandbox + subprocess fallback + threat/PII |
| 18 | **Voice/TTS** | ❌ Eksik | ❌ **Eksik** | Edge TTS var ama OpenAI TTS/STT yok |
| 19 | **Web UI** | ✅ Var | ✅ **TAM** | FastAPI+Jinja2+HTMX, auth, log stream |
| 20 | **A2A/ACP** | ⚠️ Kısmi | ⚠️ **Kısmi** | A2A broker var, ACP yok |
| 21 | **MCP Server** | ✅ Var | ✅ **TAM** | Streamable HTTP, tools/list, resources/list |
| 22 | **Tool Registry** | ✅ Var | ✅ **TAM** | check_fn TTL cache, ToolsetManager, schema override |
| 23 | **Kanban** | ✅ Var | ✅ **TAM** | Board+Card+Worker lifecycle |
| 24 | **Context Compression** | ✅ Var | ✅ **TAM** | ContextCompressor(max_token=4096) |
| 25 | **Cost Tracking** | ✅ Var | ✅ **TAM** | SQLite, session_id bazlı, model bazlı özet |
| 26 | **Self-improvement** | ✅ Var | ✅ **TAM** | SQLite metrik, trend analizi, kod kalite |
| 27 | **CLI (TUI)** | ✅ Var | ✅ **TAM** | Rich TUI, 7 mixin, 1894 satır handler |
| 28 | **Code Execution** | ✅ Var | ✅ **TAM** | Sandbox timeout, module allowlist |
| 29 | **Platform Adapter** | ✅ ReYMeN özel | ✅ **ÖZEL** | Windows/WSL/Kali — ReYMeN'te yok |

---

## 2. GERÇEK EKSİKLER (ReYMeN'te var, ReYMeN'de yok)

### ❌ Image Generation (P2)
ReYMeN'te FAL.ai / OpenAI / xAI ile görsel üretme, düzenleme, varyasyon. ReYMeN'de:
- `reymen/arac/araclar_goruntu.py` var ama FAL/OpenAI entegrasyonu yok
- Provider-agnostik image gen API yok
- **Çözüm:** `image_gen_provider.py` + FAL/OpenAI/xAI backend

### ❌ Voice/TTS/STT (P2)
ReYMeN'te OpenAI TTS, Whisper STT, sesli etkileşim. ReYMeN'de:
- Edge TTS var (basit)
- OpenAI TTS yok, Whisper STT yok
- Sesli ajan etkileşimi yok
- **Çözüm:** `voice_provider.py` + OpenAI TTS + Whisper STT

### ❌ Video Generation (P3)
ReYMeN'te video üretimi (FAL/various). ReYMeN'de:
- Hiç yok
- **Çözüm:** `video_gen_provider.py`

### ⚠️ Plugin Sistemi - Hot-reload (P2)
ReYMeN'te plugin hot-reload, dependency graph, sandbox. ReYMeN'de:
- PluginManager var, hot-reload yok
- Provider plugin (browser/image/video/tts/stt) kavramı yok
- Plugin sandbox yok
- **Çözüm:** watchdog tabanlı hot-reload + provider plugin registry

### ⚠️ ACP Protokolü (P3)
ReYMeN'te ACP (Agent Communication Protocol). ReYMeN'de:
- A2A broker var
- ACP yok
- **Çözüm:** ACP adapter

### ❌ HITL (Human-in-the-Loop) (P3)
ReYMeN'te tool call onayı, critic loop. ReYMeN'de:
- Hiç yok
- **Çözüm:** HITL pipeline + approval gate

### ❌ Skills Library / Marketplace (P3)
ReYMeN'te merkezi skill repo + sync. ReYMeN'de:
- Lokal skill yönetimi var
- Merkezi repo/paylaşım yok
- **Çözüm:** Skill repo sync + marketplace

### ❌ Multi-region / Multi-model Routing (P3)
ReYMeN'te coğrafi yönlendirme, latency-based routing. ReYMeN'de:
- Provider routing var (yeni)
- Multi-region destek yok
- **Çözüm:** Region-aware provider routing

### ❌ Docker Tam Destek (P3)
ReYMeN'te Docker container + compose + CI/CD. ReYMeN'de:
- Docker sandbox var (offline)
- Tam deployment/packaging yok
- **Çözüm:** Dockerfile + docker-compose + CI pipeline

---

## 3. ÖNCELİKLİ EKSİKLER

| Öncelik | Eksik | Zorluk | Tahmini Süre |
|---------|-------|--------|-------------|
| **P0** | ✅ **Tüm P0 tamamlandı** | - | - |
| **P1** | ✅ **Tüm P1 tamamlandı** | - | - |
| **P2** | Image Generation | Orta | 2-3 saat |
| **P2** | Voice/TTS/STT | Orta | 2-3 saat |
| **P2** | Plugin Hot-reload | Orta | 1-2 saat |
| **P3** | Video Generation | Zor | 3-4 saat |
| **P3** | ACP Protokolü | Orta | 1-2 saat |
| **P3** | HITL | Orta | 1-2 saat |
| **P3** | Skills Marketplace | Zor | 3-4 saat |
| **P3** | Docker Tam | Orta | 1-2 saat |

---

## 4. REYMeN'DE FAZLA OLANLAR (ReYMeN'te yok)

| # | Özellik | Açıklama |
|---|---------|----------|
| 1 | **Platform Adapter** | Windows/WSL/Kali yol çevirisi, platform tespiti |
| 2 | **CUA (Computer Use Agent)** | Bilgisayar kullanımı için motor aracı |
| 3 | **Hook Dispatcher** | Async event-driven TOOL_CALLED/TOOL_ERROR sistemi |
| 4 | **Hata Sınıflandırıcı + Mesaj Tamirci** | API hatalarını sınıflandırma, tool call tamiri |
| 5 | **MessageBroker** | queue.Queue tabanlı pipeline görev çözümü |
| 6 | **Türkçe Dil Desteği** | Türkçe değişken/fonksiyon isimleri, dokümantasyon |
| 7 | **Paylaşımlı durum.json** | Tüm botların ortak durum dosyası |

---

## 5. İSTATİSTİK

- **Toplam özellik:** 29
- **✅ Tamam:** 24/29 (%83)
- **⚠️ Kısmi:** 2/29 (%7) — Plugin hot-reload, ACP
- **❌ Eksik:** 3/29 (%10) — Image Gen, Voice/TTS, Video Gen
- **ReYMeN özel:** 7 özellik (ReYMeN'te yok)
