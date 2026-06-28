# ReYMeN — Geliştirme Task'ı

## Mevcut Durum
Aşağıdaki yapılar kuruldu. İncele, geliştir ve eksikleri tamamla.

### ✅ KURULU
| Bileşen | Dosya | Açıklama |
|---------|-------|----------|
| Model Adapter | `reymen/core/model_adapter.py` | 7 provider (Ollama, LM Studio, GLM, DeepSeek, OpenAI, Anthropic, Gemini), auto-detect |
| Orchestrator | `reymen/core/orchestrator.py` | solve_step(), solve_all(), coz_hata(), 3 retry, JSONL log |
| Öğrenme Döngüsü | `reymen/core/ogrenme.py` | CozumHafizasi (hata→çözüm), OgrenmeDongusu (hafıza→LLM→kaydet) |
| Motor entegrasyonu | `reymen/cereyan/motor.py` | ogren(), ogrenme_istatistik(), gorev_coz(), hatadan_kurtul() |
| pyproject.toml | `./pyproject.toml` | Build, bağımlılıklar, pytest+ruff+bandit |
| Docker | `./Dockerfile`, `./docker-compose.yml` | Container ortamı |
| Skill import | `reymen/scripts/skill_import.py` | Hermes→ReYMeN skill dönüştürücü |

### ❌ GELİŞTİRİLMESİ GEREKENLER

#### 1. MCP Server Host
- Mevcut: `agent/transports/mcp.py` (transport katmanı)
- Eksik: ReYMeN'in kendi MCP sunucusu (diğer MCP client'larının bağlanabileceği)
- Yapılacak: `reymen/core/mcp_server.py` — diğer agent'ların tool çağırabileceği MCP host

#### 2. Session Search (FTS5)
- Mevcut: `.ReYMeN/session.db` (SQLite)
- Eksik: FTS5 full-text search, session_search_tool.py
- Yapılacak: `reymen/core/session_search.py` — Hermes'teki gibi FTS5 ile hızlı arama

#### 3. Web UI
- Mevcut: `dashboard/app.py` (basit dashboard)
- Eksik: Hermes Web UI seviyesinde arayüz
- Yapılacak: `dashboard/`'i geliştir — görev takibi, log görüntüleme, öğrenme istatistikleri

#### 4. Öğrenme Döngüsü İyileştirmeleri
- `motor.calistir()` içinde try/except ile hata yakalayıp `ogren()`'e yönlendir
- CozumHafizasi'na TTL ekle (eski çözümleri temizle)
- OgrenmeDongusu'na retry backoff ekle

## ÖNCELİK SIRASI
1. MCP Server Host (diğer araçların bağlanması için)
2. Session Search FTS5 (hızlı geçmiş arama)
3. Öğrenme döngüsü iyileştirmeleri
4. Web UI

## KISITLAMALAR
- shell=True KULLANMA
- Her adımda pytest ile doğrula
- Hata alırsan düzeltip tekrar dene (max 3)
- Logları `logs/` altına kaydet
