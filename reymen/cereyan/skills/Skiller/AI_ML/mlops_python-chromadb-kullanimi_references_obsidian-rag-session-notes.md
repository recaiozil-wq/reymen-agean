---
name: mlops_python-chromadb-kullanimi_references_obsidian-rag-session-notes
description: Obsidian Vault → ChromaDB RAG — Bulgular ve Referans
title: "Mlops Python Chromadb Kullanimi References Obsidian Rag Session Notes"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Obsidian Vault → ChromaDB RAG — Bulgular ve Referans |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Obsidian Vault → ChromaDB RAG — Bulgular ve Referans

Bu oturumda 791 .md dosyası taranıp 788'i indexlendi. Kullanılan araçlar ve sonuçlar:

## Teknik Detaylar

- **Embedding modeli:** Ollama `nomic-embed-text` (Türkçe için en başarılı yerel model)
- **Vektör DB:** ChromaDB v1.x (Rust backend, `PersistentClient`)
- **Dosya sayısı:** 791 .md dosya tarandı → 788 doküman indexlendi (3 boş dosya atlandı)
- **DB yolu:** `C:\Users\marko\AppData\Local\hermes\obsidian_rag_db`
- **Batch boyutu:** 50 doküman/batch
- **Token limit:** 3000 char/doküman

## Sorgu Performansı

| Sorgu | Süre | En iyi skor |
|-------|------|-------------|
| "Hermes nedir hangi modelleri kullanir" | ~3s | 0.294 |
| "yapay zeka nedir obsidian" | ~3s | 0.637 |
| "hermes agent nasil calisir hangi ozellikler var" | ~3s | 0.705 |

Not: Legacy skill'ler (Skills-legacy klasörü) daha yüksek puan alır çünkü embedding "hermes/agent" gibi kelimeleri metin içinde barındırır. Asıl anlamlı sonuçlar için "yapay zeka", "bilim", "felsefe" gibi kavramsal sorgular daha iyi.

## Embedding Function ChromaDB Uyumluluğu

ChromaDB v1.x, custom embedding function'dan 3 metod bekler:
1. `name() -> str` — collection metadata'ya kaydedilir
2. `embed_query(input)` — query'de çağrılır; parametre ADI `input` olmalı, tipi belirtilmemiş olmalı
3. `__call__(input: list[str]) -> list[list[float]]` — add/update'de batch çağrılır

## Ollama API v0.24+

- Endpoint: `POST /api/embed` (plural `s`)
- Request: `{"model": "nomic-embed-text", "input": "metin"}` veya `{"input": ["m1", "m2", "m3"]}`
- Response: `{"model": "...", "embeddings": [[...], [...], ...]}`
- Eski API (`/api/embeddings` + `"prompt"` key) → 500 Internal Server Error

## Obsidian Wiki Dizini

Wiki yapısı: `C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\wiki\`
- SCHEMA.md — entity şeması (6 tip: concept, person, tool, project, daily, book)
- index.md — ana navigasyon
- log.md — değişiklik takibi
- 19 entity sayfası (Concept/, Person/, Tool/, Project/, Book/)

## Kullanılan Scriptler

- `scripts/obsidian_rag.py` — full index + query CLI
- `scripts/rag_query.py` — sadece sorgu (daha hafif)
