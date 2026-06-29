---
name: software-development_reymen-proje-mimarisi_references_session-table-schema
description: Hermes Agent Sessions Tablo Schema
title: "Software Development Reymen Proje Mimarisi References Session Table Schema"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Hermes Agent Sessions Tablo Schema |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Hermes Agent Sessions Tablo Schema

## CREATE TABLE

```sql
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    user_id TEXT,
    model TEXT,
    model_config TEXT,
    system_prompt TEXT,
    parent_session_id TEXT,
    started_at REAL NOT NULL,
    ended_at REAL,
    end_reason TEXT,
    message_count INTEGER DEFAULT 0,
    tool_call_count INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cache_read_tokens INTEGER DEFAULT 0,
    cache_write_tokens INTEGER DEFAULT 0,
    reasoning_tokens INTEGER DEFAULT 0,
    billing_provider TEXT,
    billing_base_url TEXT,
    billing_mode TEXT,
    estimated_cost_usd REAL,
    actual_cost_usd REAL,
    cost_status TEXT,
    cost_source TEXT,
    pricing_version TEXT,
    title TEXT,
    api_call_count INTEGER DEFAULT 0,
    FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
);
```

## Indexes

```sql
CREATE INDEX IF NOT EXISTS idx_sessions_source ON sessions(source);
CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC);
CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_title_unique
    ON sessions(title) WHERE title IS NOT NULL;
```

## Sutun Aciklamalari

| Sutun | Tip | Aciklama |
|-------|-----|----------|
| id | TEXT PRIMARY KEY | UUID |
| source | TEXT NOT NULL | cli, telegram, discord, api... |
| user_id | TEXT | Platform kullanici ID |
| model | TEXT | Model adi (deepseek, gpt-4...) |
| model_config | TEXT | JSON model yapilandirmasi |
| system_prompt | TEXT | Kullanilan sistem prompt |
| parent_session_id | TEXT | Zincirleme session (FOREIGN KEY) |
| started_at | REAL | Unix timestamp |
| ended_at | REAL | Unix timestamp (NULL = devam ediyor) |
| end_reason | TEXT | completed, cancelled, error, interrupted |
| message_count | INTEGER | Toplam mesaj sayisi |
| tool_call_count | INTEGER | Kac tool cagrisi yapildi |
| input_tokens | INTEGER | Toplam input token |
| output_tokens | INTEGER | Toplam output token |
| cache_read_tokens | INTEGER | Anthropic cache hit |
| cache_write_tokens | INTEGER | Anthropic cache write |
| reasoning_tokens | INTEGER | Reasoning token (DeepSeek, o1) |
| billing_provider | TEXT | Fatura kesen provider |
| billing_base_url | TEXT | Provider base URL |
| billing_mode | TEXT | pay-as-you-go, subscription, free |
| estimated_cost_usd | REAL | Tahmini maliyet |
| actual_cost_usd | REAL | Gercek maliyet (API'den donduyse) |
| cost_status | TEXT | estimated, actual, pending, unavailable |
| cost_source | TEXT | Hangi pricing tablosundan hesaplandi |
| pricing_version | TEXT | Pricing tablosu versiyonu |
| title | TEXT | Session basligi (otomatik) |
| api_call_count | INTEGER | Kac API cagrisi yapildi |

## ReYMeN'deki Mevcut Durum

ReYMeN'in session_db.py (125 satir) sadece FTS5 ajan_gunlugu tablosu var.
Session yok, token/maliyet takibi yok, parent iliskisi yok.

Yapilmasi gereken:
- Yukaridaki sessions tablosu ekle
- Mevcut FTS5 ajan_gunlugu tablosu da dursun (geriye uyumluluk)
- WAL mode: PRAGMA journal_mode=WAL
- Thread-safe baglanti

Detayli task: `SESSION_UPDATE_TASK.md`
