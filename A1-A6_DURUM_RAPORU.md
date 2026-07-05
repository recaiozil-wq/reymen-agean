# ReYMeN → Hermes Bağımsızlaştırma Durum Raporu

Tarih: 2026-07-04
Proje: `C:\Users\marko\Desktop\Reymen Proje\ReYMeN-Ajan\`

---

## SONUÇ ÖZETİ

| Adım | Ad                 | Durum    | İlerleme |
|------|---------------------|----------|----------|
| A1   | Kod referans temizle | BAŞLAMADI | 0%       |
| A2   | hermes_stubs birleştir | BAŞLAMADI | 0%       |
| A3   | Gateway altyapısı    | KISMİ    | ~30%     |
| A4   | LLM çağrı mekanizması | KISMİ    | ~70%     |
| A5   | Web search + tool'lar | KISMİ    | ~50%     |
| A6   | Config/session taşıma | KISMİ    | ~40%     |

---

## A1 — Kod Referanslarını Temizle: BAŞLAMADI

**943 "hermes" referansı** hala tüm src/ ağacında mevcut.
**23 dosya** hala `from src.reymen.cron.hermes_stubs import ...` yapıyor.

### Etkilenen dosyalar (tam liste):

| Dosya | Import | Ne alıyor |
|-------|--------|-----------|
| `src/gateways/config.py:19-20` | hermes_stubs | get_hermes_home, is_truthy_value |
| `src/gateways/session.py:68` | hermes_stubs | atomic_replace |
| `src/gateways/status.py:23,25` | hermes_stubs | get_hermes_home, atomic_json_write |
| `src/gateways/delivery.py:19` | hermes_stubs | get_hermes_home |
| `src/gateways/hooks.py:46` | hermes_stubs | get_hermes_home |
| `src/gateways/mirror.py:17` | hermes_stubs | get_hermes_home |
| `src/gateways/whatsapp_identity.py:45` | hermes_stubs | get_hermes_home |
| `src/gateways/sticker_cache.py:17` | hermes_stubs | get_hermes_home |
| `src/gateways/slash_commands.py:32-41` | hermes_stubs | account_usage, i18n, cfg_get, ... |
| `src/gateways/platforms/base.py:23,530` | hermes_stubs | normalize_proxy_url, +10 fonk |
| `src/gateways/platforms/telegram.py:97` | hermes_stubs | atomic_replace |
| `src/gateways/platforms/helpers.py:16` | hermes_stubs | atomic_json_write |
| `src/gateways/platforms/matrix.py:59` | hermes_stubs | ensure |
| `src/gateways/platforms/signal.py:58` | hermes_stubs | ensure |
| `src/reymen/cron/scheduler.py:36` | hermes_stubs | (çoklu import) |
| `src/reymen/cron/jobs.py:33` | hermes_stubs | (çoklu import) |
| `src/reymen/cron/cronjob_tool.py:15` | hermes_stubs | display_hermes_home |

### Yapılması gereken:
1. `hermes_stubs/__init__.py`'deki fonksiyon adlarını değiştir: `get_hermes_home` → `get_reymen_home`
2. `hermes_uyum.py`'deki "Hermes" adlarını temizle
3. Tüm 23 import noktasını güncelle
4. String/yorum referanslarını "ReYMeN" ile değiştir

---

## A2 — hermes_stubs + hermes_uyum Birleştirme: BAŞLAMADI

### Mevcut durum:
- `src/reymen/cron/hermes_stubs/__init__.py` — 329 satır, ~30 stub fonksiyon
- `src/reymen/cron/hermes_stubs/config.py` — 76 satır
- `src/reymen/cron/hermes_stubs/account_usage.py` — 55 satır
- `src/reymen/cron/hermes_stubs/i18n.py` — 46 satır
- `src/reymen/sistem/hermes_uyum.py` — 126 satır, 8 fonksiyon

### Eksik olan (planlanan ama yazılmayan):
- `src/reymen/sistem/reymen_stubs.py` — **YOK** (henüz oluşturulmamış)
- SessionDB wrapper — **YOK**
- `_get_platform_tools` stub — **YOK**
- `kanban_db` stub — **YOK**
- `env_passthrough` stub — **YOK**

### Yapılması gereken:
1. 5 dosyayı tek bir `reymen_stubs.py`'de birleştir
2. 4 eksik stub'ı ekle
3. Eski `hermes_stubs/` dizinini sil
4. 23 import noktasını `from reymen.sistem.reymen_stubs import ...` olarak güncelle

---

## A3 — Gateway Altyapısı: KISMİ (~30%)

### Mevcut olan:
| Dosya | Satır | Durum |
|-------|-------|-------|
| `scripts/reymen_gateway.py` | 122 | Basit launcher, TelegramAdapter import ediyor ama polling başlatmıyor |
| `src/gateways/gateway_runner.py` | 1054 | Gelişmiş runner, çoklu kanal desteği var, Hermes bağımlı değil |
| `src/gateways/platforms/telegram.py` | ~1000+ | python-telegram-bot kullanıyor, ama hermes_stubs import var |
| `src/gateways/config.py` | 2,467 | Config yüklüyor, ama get_hermes_home'e bağımlı |
| `src/gateways/session.py` | 1,566 | Session yönetimi var, atomic_replace'e bağımlı |

### Eksik olan:
- `reymen_gateway.py` hala sadece import ediyor, **polling başlatmıyor**
- Gateway'ı tamamen Hermes'siz başlatan bir entry point yok
- Health check mekanizması eksik
- Cron job'lar hala Hermes scheduler'a bağımlı

### Yapılması gereken:
1. `reymen_gateway.py`'yi tam çalışır hale getir (polling + webhook)
2. `gateway_runner.py`'yi Hermes imports'tan kurtar
3. Health check ekle
4. `reymen.bat`'ı güncelle: `hermes -p reymen gateway run` → `python reymen_gateway.py`

---

## A4 — LLM Çağrı Mekanizması: KISMİ (~70%)

### Mevcut olan:
| Dosya | Satır | Durum |
|-------|-------|-------|
| `src/core/provider_abstraction.py` | 1,679 | **Tam bağımsız** — DeepSeek, OpenAI, Anthropic, Groq, Xiaomi, xAI, OpenRouter, LMStudio destekli |
| `src/core/model_provider.py` | 833 | **Tam bağımsız** — ProviderChain + failover |
| `src/gateways/litellm_provider.py` | — | LiteLLM entegrasyonu |
| `src/gateways/provider_router.py` | — | Provider yönlendirme |
| `src/gateways/model_provider_router.py` | — | Model routing |

### Eksik olan (planlanan ama farklı isimlerle var):
| Planlanan | Mevcut | Durum |
|-----------|--------|-------|
| `core/llm_caller.py` | `core/provider_abstraction.py` | FARKLI DOSYA — ama aynı işi yapıyor |
| `providers/deepseek.py` | `provider_abstraction.py` içinde DeepSeekProvider | **İÇ İÇE** — ayrı dosya yok |
| `providers/xiaomi.py` | provider_abstraction.py içinde | Aynı |
| `providers/openrouter.py` | provider_abstraction.py içinde | Aynı |
| `providers/lmstudio.py` | provider_abstraction.py içinde | Aynı |
| `core/fallback_chain.py` | `core/model_provider.py` ProviderChain | Aynı iş, farklı isim |
| Token sayacı | `src/reymen/cost_tracker.py` (478 satır) | **VAR** |

### Yapılması gereken:
1. Provider'ları ayrı dosyalara böl (opsiyonel — mevcut yapı çalışıyor)
2. Gateway'den LLM çağrısını entegre et (gateway → provider_abstraction → LLM)

---

## A5 — Web Search + Tool'lar: KISMİ (~50%)

### Mevcut olan:
| Dosya | Satır | Durum |
|-------|-------|-------|
| `src/reymen/tools/web_tools.py` | 429 | **Tam bağımsız** — Firecrawl, Tavily, Exa, Brave, SearXNG, Parallel |
| `src/reymen/web_search_registry.py` | 130 | Backend seçim mantığı |
| `src/reymen/web_search_provider.py` | 57 | Provider arayüzü |
| `src/reymen/sistem/tools_registry.py` | 532 | **Tam bağımsız** — merkezi tool kayıt sistemi |
| `src/reymen/tools/approval.py` | 37 | Onay mekanizması (basit shim) |
| `src/reymen/tools/terminal_tool.py` | — | Terminal erişimi (var) |
| `src/reymen/tools/file_tools.py` | — | Dosya okuma/yazma (var) |

### Eksik olan:
- Tool registry gateway ile entegre değil (gateway → tool çağrısı zinciri eksik)
- Onay mekanizması çok basit (smart/strict modları yok)

### Yapılması gereken:
1. Gateway'den tool_registry'ye çağrı zincirini kur
2. Approval middleware'i güçlendir (smart/strict mod)

---

## A6 — Config/Session Bağımsızlaştırma: KISMİ (~40%)

### Mevcut olan:
| Dosya | Satır | Durum |
|-------|-------|-------|
| `src/reymen/sistem/ReYMeN_constants.py` | 466 | **`get_reymen_home()` ZATEN VAR** — 30 kullanım noktası |
| `src/core/config_manager.py` | 537 | Config yönetimi var |
| `src/core/session_db.py` | 164 | Session DB var |
| `scripts/reymen_gateway.py` | 122 | Gateway launcher (ama tam çalışmıyor) |

### Eksik olan:
| Planlanan | Durum |
|-----------|-------|
| `src/core/reymen_home.py` | **YOK** — ama `ReYMeN_constants.py` içinde `get_reymen_home()` zaten var |
| `reymen.bat` güncelleme | **YAPILMAMIŞ** — hala `hermes -p reymen gateway run` kullanıyor |
| Config merge | Kısmen var (config_manager.py) |
| Cron job taşıma | Hala Hermes scheduler'a bağımlı |

### Yapılması gereken:
1. `reymen.bat`'ı güncelle
2. Config dosyalarını `~/.reymen/` altına taşı
3. Cron job'ları Python schedule ile yeniden yaz

---

## KRİTİK BAGLANTILAR

```
reymen.bat (A6) → reymen_gateway.py (A3)
  ├── hermes_stubs (A1/A2) ← 23 dosya bağımlı
  ├── provider_abstraction (A4) ← çalışıyor
  ├── tools_registry (A5) ← çalışıyor
  └── ReYMeN_constants (A6) ← çalışıyor
```

### En kritik darboğaz: A1/A2
23 dosya `hermes_stubs` import ediyor. Bunlar düzeltilmeden gateway çalışmaz.

---

## ÖNERİLEN SIRA

```
A2 (birleştir) → A1 (temizle) → A3 (gateway) → A6 (entry point)
                     ↑                               ↑
               A4 ve A5 zaten çalışıyor         reymen.bat güncelle
```

1. **Önce A2**: `reymen_stubs.py` oluştur, 5 dosyayı birleştir
2. **Sonra A1**: 23 import noktasını güncelle, hermes referanslarını sil
3. **Sonra A3**: Gateway'ı tam çalışır hale getir
4. **En sonda A6**: Entry point ve config taşıma

**A4 ve A5 zaten büyük ölçüde hazır** — sadece entegrasyon eksik.
