---
name: ReYMeN-proje-benchmark
description: ReYMeN projesinin guncel metrikleri - 755 .py, 215K satir, 29/32 ozellik tamam, Hermes karsilastirma gap analizi
category: genel
audience: maintainer
tags: [benchmark, metrics, quality, gap-analysis, comparison]
title: ReYMeN Proje Benchmark
version: 1.0.0
---

# ReYMeN Proje Benchmark

## Genel Metrikler (29 Haziran 2026 — Guncel)

| Metrik | Deger |
|--------|-------|
| Python dosyasi | **755** |
| Toplam kod satiri | **214,596** |
| Test dosyasi | **92** |
| Test satiri | **9,480** |
| Coverage | **~%4.4** |
| ✅ Mevcut ozellik | **29/32** |
| ❌ Tamamen eksik | **8** (Dokumantasyon sitesi, MCP Server Host, Plugin Marketplace, Kanban Worker, Voice Pipeline, Video Gen, Community Repo, Hot Reload) |
| ⚠️ Kismen/stub | **5** (Provider plugin tool kaydi, Test Coverage %60 hedef, TTS tool, Session Search motor aracı, Desktop dogrulama) |
| En buyuk modul | `reymen_cli/main.py` — 14,988 satir |
| En karmasik modul | `reymen/ag/delegasyon.py` — 46,139 bytes / ~1,800 satir |

> Detayli gap analizi ham verisi icin: `references/hermes-gap-analizi-2026-06-29.md`

### Hermes vs ReYMeN — Ozellik Karsilastirmasi

| # | Ozellik | ReYMeN | Hermes | Fark |
|---|---------|--------|--------|------|
| 1 | **Provider LiteLLM** | ✅ (19 provider) | ✅ (30+) | Yakın |
| 2 | **Model Failover** | ✅ (10 hata kategorisi) | ✅ | Eşit |
| 3 | **Profile Manager** | ✅ (4 profil) | ✅ | Eşit |
| 4 | **Session DB (FTS5)** | ✅ (hafiza/) | ✅ | Eşit |
| 5 | **Cron/Scheduler** | ✅ (cronjob tool) | ✅ | Eşit |
| 6 | **Gateway Sistemi** | ✅ (5 dosya) | ✅ (28 platform) | Eşit |
| 7 | **Vector Memory** | ✅ (ChromaDB+SQLite) | ✅ | Eşit |
| 8 | **OAuth 2.0** | ✅ (Google/GitHub/Discord) | ✅ | Eşit |
| 9 | **Delegasyon** | ✅ (46KB modul) | ✅ | Eşit |
| 10 | **Guardrails** | ✅ (threat+PII) | ✅ | Eşit |
| 11 | **Plugin Sistemi** | ✅ (7 plugin) | ✅ | Yakın |
| 12 | **Web UI** | ✅ (22 template) | ✅ | Eşit |
| 13 | **Desktop Uygulama** | ✅ (6 dosya) | ✅ | Dogrulanmadi |
| 14 | **A2A** | ✅ (4 dosya) | ✅ | Eşit |
| 15 | **Self Improve** | ✅ (SQLite, 68 kayit) | ✅ | Eşit |
| 16 | **Continuous Learning** | ✅ (session arasi) | ✅ | Eşit |
| 17 | **Kost Tracker** | ✅ (15KB) | ✅ | Eşit |
| 18 | **Test Coverage** | ❌ %4.4 | ✅ %60 | **%55 eksik** |
| 19 | **Dokumantasyon Sitesi** | ❌ README+API.md | ✅ docs.nousresearch.com | **Tamamen eksik** |
| 20 | **TTS/STT Tool** | ❌ ReYMeN'de yok | ✅ edge-tts+Whisper | **Tamamen eksik** |
| 21 | **MCP Server Host** | ❌ Yok | ✅ | **Tamamen eksik** |
| 22 | **Video Generation** | ❌ Yok | ✅ | **Tamamen eksik** |

### Esitlenme Durumu

| Alan | Gecmis (16 Haz) | Guncel (29 Haz) | Degisim |
|------|----------------|-----------------|---------|
| Python dosyasi | 152 | **755** | 🚀 +603 |
| Test dosyasi | 42 | **92** | 📈 +50 |
| Ozellik tamam | ~%70 | **%90** (%29/32) | 📈 +%20 |
| Provider plugin | 2 | **19** (LiteLLM) | 🚀 +17 |
| Gateway | 28 | **5 dosya** | 🔄 Yeniden yapilandirildi |
| Plugin | 1 (merhaba) | **7** | 📈 +6 |

### ReYMeN'e Özgü Güçlü Yanlar

PUAN = satir/10 + fonk*2. En buyuk moduller:

| Modül | Konum | Satir |
|-------|-------|-------|
| reymen_cli/main.py | `reymen/reymen_cli/main.py` | 14,988 |
| run_agent.py | `reymen/sistem/run_agent.py` | 4,858 |
| provider_cmds.py | `reymen/reymen_cli/provider_cmds.py` | 4,090 |
| cli_tui.py | `reymen/sistem/cli_tui.py` | 3,983 |
| ReYMeN_state.py | `reymen/sistem/ReYMeN_state.py` | 3,971 |
| web_ui/__init__.py | `reymen/web_ui/__init__.py` | 3,414 |
| session_commands.py | `reymen/sistem/cli_commands/session_commands.py` | 3,347 |
| cli_main.py | `reymen/sistem/cli_main.py` | 3,280 |
| conversation_loop.py | `reymen/cereyan/conversation_loop.py` | 2,515 |
| motor.py | `reymen/cereyan/motor.py` | 2,314 |

## Kalan Eksikler ve Öncelik Sirasi

### 8 Tamamen Eksik (Hermes'te var)

| P0 | Özellik | ReYMeN | Hermes |
|:--:|---------|--------|--------|
| 🔴 | **Dokümantasyon Sitesi** | README + API.md | docs.nousresearch.com |
| 🔴 | **Test Coverage (%4 → %60)** | 92 test / 9,480 satır | 1000+ test |
| 🟠 | **TTS + STT Tool** (ReYMeN'de) | edge-tts kurulu ama tool yok | edge-tts + Whisper |
| 🟡 | **MCP Server Host** | Yok | MCP sunucu hosting |
| 🟡 | **Kanban Worker** | Yok | Worker döngüsü |
| 🟡 | **Video Generation** | Yok | Video üretimi |
| 🔵 | **Plugin Marketplace** | Yok | Store sistemi |
| 🔵 | **Hot Reload** | Yok | Runtime değişiklik algılama |

### 5 Kısmen Var (Stub/Eksik Entegrasyon)

| Özellik | Durum | Ne Gerekli? |
|---------|-------|-------------|
| Provider Plugin'leri | 6 plugin stub, tool kaydı yok | `__init__.py`'ye motor aracı kaydı |
| TTS (edge-tts) | Kurulu ama ReYMeN tool'u yok | `reymen/sistem/tts_tool.py` |
| Session Search | `core/` + `sistem/` var ama motor tool'u yok | Motor'a SESSION_ARA aracı |
| Desktop Uygulama | 6 dosya (17KB) | Doğrulama + test |
| Kalite Dashboard | `quality.html` var | coverage+cron verisi canlı |

## Duzgun Calisan Ozellik Detaylari (29 Haziran 2026)

Asagidaki ozelliklerin her biri dosya olarak var, motor'a kayitli ve conversation_loop'a bagli:

| Ozellik | Konum | Boyut | Entegrasyon |
|---------|-------|-------|-------------|
| Provider LiteLLM | `reymen/ag/litellm_provider.py` | 7KB | motor.py PROVIDER_ araclari |
| Model Failover | `reymen/ag/failover_chain.py` | 11KB | motor.py PROVIDER_ZINCIR |
| Profile Manager | `reymen/sistem/profile_manager.py` | 10KB | motor.py PROFIL_ araclari |
| Vektor Bellek | `reymen/hafiza/vektor_bellek.py` | 18KB | motor.py VECTOR_ araclari |
| OAuth 2.0 | `reymen/guvenlik/oauth_sistemi.py` | 38KB | motor.py OAUTH_ araclari |
| Guardrails | `reymen/guvenlik/guardrails.py` | 14KB | threat+PII tespiti |
| Delegasyon | `reymen/ag/delegasyon.py` | 46KB | conversation_loop hook |
| Gateway Sistemi | `reymen/ag/gateway_*.py` (5 dosya) | 4-30KB | motor.py GATEWAY_ araclari |
| Cron Scheduler | `reymen/sistem/cron_scheduler.py` | 15KB | cronjob tool |
| Docker Sandbox | `reymen/guvenlik/docker_sandbox.py` | 20KB | subprocess fallback |
| Web UI | `reymen/web_ui/` (22 template) | 141KB | FastAPI, 9 route |
| Self Improve | `reymen/self_improve.py` | 29KB | SQLite, 68 kayit |
| Continuous Learning | `reymen/cereyan/continuous_learning.py` | 11KB | session arasi context |

### ReYMeN'e Özgü Güçlü Yanlar

| Özellik | Dosya | Neden Güçlü |
|---------|-------|-------------|
| Ekran OCR + tıkla | `araclar_ekran.py` | Windows otomasyon — Hermes'te yok |
| Makro kaydet/oynat | `araclar_makro.py` | Benzersiz özellik |
| Kapalı öğrenme döngüsü | `closed_learning_loop.py` | Otomatik beceri geliştirme |
| Motor+Beyin mimarisi | `motor.py`, `beyin.py` | Ayrık ReAct — esnek |
| 22 Web UI template | `reymen/web_ui/templates/` | deployment, cron, gateway, media, vb. |
| Session search (FTS5) | `reymen/core/session_search.py` (11KB) + `sistem/session_search_tool.py` (5KB) | trigram + tarih filtreli |
