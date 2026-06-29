---
name: software-development_project-startup-check_references_odysseus-mimari-analiz
description: Odysseus — Mimari Analiz Referansı
title: "Software Development Project Startup Check References Odysseus Mimari Analiz"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Odysseus — Mimari Analiz Referansı |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Odysseus — Mimari Analiz Referansı

Aşağıdaki analiz 11 Haziran 2026'da yapılmıştır. Odysseus v1.0, Piebie/PewDiePie tarafından 31 Mayıs 2026'da yayınlanmıştır.

## Kök Dizin Yapısı

```
odysseus/
├── app.py               # FastAPI orkestratörü (1145 satır)
├── .env.example         # Yapılandırma şablonu
├── pyproject.toml       # Python proje tanımı (pytest config)
├── requirements.txt     # Bağımlılıklar
├── requirements-optional.txt
├── Dockerfile           # Container build
├── docker-compose.yml   # 4 container stack
├── package.json         # npm (frontend bağımlılıkları için)
├── README.md            # 469 satır dokümantasyon
└── ROADMAP.md           # Geliştirme yol haritası
```

## Katman Haritası

| Klasör | Boyut | İçerik |
|--------|-------|--------|
| `core/` | 10 dosya (~190KB) | auth, database (SQLAlchemy), session_manager, middleware, constants, models, exceptions |
| `routes/` | 57 dosya (~1.8MB) | Tüm API endpoint'leri — en büyükler: cookbook_routes (164KB), email_routes (160KB), model_routes (104KB) |
| `src/` | ~95 dosya (~2MB) | İş mantığı — en büyükler: tool_implementations (191KB), agent_loop (190KB), llm_core (105KB), task_scheduler (113KB) |
| `services/` | 9 alt klasör | memory, search, hwfit, research, docs, shell, stt, tts, youtube |
| `static/` | ~80+ JS dosya (~1.6MB) | SPA frontend — index.html (211KB), app.js (179KB), style.css (1.2MB!) |

## Mimari Model

- **Monolith SPA** + **Microservice hybrid**
- FastAPI backend, vanilla JS frontend (framework yok, modular JS)
- Docker Compose ile 4 container: odysseus (ana) + searxng (arama) + chromadb (vektör) + ntfy (bildirim)
- SQLite (SQLAlchemy ORM) + ChromaDB (vektör DB)
- REST API (FastAPI routes) + SSE stream (chat, shell, research)

## Tespit Edilen Pattern'ler

1. **Tek dosyada toplanmış büyük modüller** — agent_loop.py (190KB), tool_implementations.py (191KB) — refactor adayı
2. **Önce auth, sonra her şey** — auth sistemi core/auth.py'de, her route'a middleware ile bağlı
3. **SPA frontend** — tek index.html + app.js + modular JS/ altında 80+ dosya. CSS tek dosyada 1.2MB
4. **ChromaDB + SQLite ikilisi** — session/document için SQLite, vektör arama için ChromaDB
5. **Docker Compose dependency chain** — odysseus → searxng (healthcheck) + chromadb (started)

## Geliştirme için Çıkarımlar

- Yeni bir özellik eklemek: routes/ → yeni dosya + app.py'ye register + src/ iş mantığı + static/js/ frontend
- Frontend değişikliği: index.html (HTML yapısı) + app.js (ana JS) + js/ altında ilgili modül
- Backend değişikliği: src/ iş mantığı, routes/ API katmanı
- Container değişikliği: docker-compose.yml + Dockerfile
