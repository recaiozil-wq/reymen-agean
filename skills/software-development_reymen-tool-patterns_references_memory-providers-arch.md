---
name: software-development_reymen-tool-patterns_references_memory-providers-arch
description: Bellek Sagleci Mimarisi (4 Provider)
title: "Software Development Reymen Tool Patterns References Memory Providers Arch"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bellek Sagleci Mimarisi (4 Provider) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bellek Sagleci Mimarisi (4 Provider)

## Klasor Yapisi

```
tools/memory_providers/
  __init__.py               # from .memory_bridge import run, motor_kaydet
  base.py                   # ABC BellekSaglayici interface
  file_provider.py          # JSON dosya (atomic write, bozuk dosya recovery)
  chromadb_provider.py      # ChromaDB vektor (upsert, count guard, hnsw:cosine)
  sqlite_provider.py        # SQLite + FTS5 (executescript DDL, LIKE fallback)
  redis_provider.py         # Redis (TTL, SCAN iterator, decode_responses=True)
  memory_bridge.py          # Thread-safe bridge (threading.Lock, frozenset)
```

## Provider Testi

```python
# File (her zaman calisir)
run("file", "kaydet", "a1", "deger")
run("file", "oku", "a1")
run("file", "ara", sorgu="deger")
run("file", "durum")
run("file", "sil", "a1")

# SQLite (her zaman calisir, FTS5 yoksa LIKE fallback)
run("sqlite", "kaydet", "a1", "deger")
run("sqlite", "ara", sorgu="deger")

# ChromaDB (gerektirir: pip install chromadb)
run("chromadb", "durum")  # graceful degrade

# Redis (gerektirir: pip install redis, redis server)
run("redis", "durum")  # graceful degrade
```

## Onemli Pattern'ler

1. **ABC Interface**: Tum provider'lar `BellekSaglayici`'dan turer, 5 method: kaydet/oku/ara/sil/durum
2. **Graceful Degrade**: `_aktif=False` + `_hata_msg` + `_guard()` — provider calismazsa crash yok
3. **Lazy Singleton**: `_get_saglayici()` thread-safe lock ile tek instance
4. **Atomic Write**: File provider `tempfile.mkstemp()` + `os.replace()` — crash'te yari-yazili dosya kalmaz
5. **SQLite DDL**: Trigger'lar noktali virgul icerdigi icin `executescript()` kullan, `split(";")` ile parcailama
6. **Redis SCAN**: Cursor-based iterator, buyuk keyspace'te RAM spike yok
7. **Frozenset Guard**: Gecersiz tur/eylem icin `frozenset` ile hizli kontrol
