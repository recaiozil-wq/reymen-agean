---
name: software-development_reymen-proje-mimarisi_references_memory-providers
description: Bellek Sagleci Sistemi (4 Provider)
title: "Software Development Reymen Proje Mimarisi References Memory Providers"
version: 1.0.0
---


| 5N1K | Açıklama |
|:----:|:---------|
| **Kim** | AI/ML mühendisi |
| **Ne** | Bellek Sagleci Sistemi (4 Provider) |
| **Nerede** | AI_ML/ |
| **Ne Zaman** | AI/ML görevi gerektiğinde |
| **Neden** | standardize etmek için |
| **Nasıl** | Skill adımlarını takip ederek |

# Bellek Sagleci Sistemi (4 Provider)

## Klasor
```
tools/memory_providers/
  __init__.py               # from .memory_bridge import run, motor_kaydet
  base.py                   # ABC BellekSaglayici
  file_provider.py          # JSON dosya (atomic write)
  chromadb_provider.py      # ChromaDB vektor (upsert)
  sqlite_provider.py        # SQLite + FTS5 (executescript)
  redis_provider.py         # Redis TTL (SCAN iterator)
  memory_bridge.py          # Thread-safe singleton bridge
```

## Entegrasyon
- Motor'a kayit: `"tools.memory_providers"` → `_plugin_moduller_yukle()` cagirir
- `motor_kaydet()` → `MEMORY_PROVIDER` olarak kaydeder
- Eylemler: kaydet, oku, ara, sil, durum

## Kritik Pattern'ler
1. ABC interface: tum provider'lar `BellekSaglayici`'dan turer (kaydet/oku/ara/sil/durum)
2. Graceful degrade: `_aktif=False` + `_hata_msg` + `_guard()` — crash yok
3. Thread-safe singleton: `threading.Lock` ile `_SAGLAYICILAR` dict korumasi
4. Atomic write: `tempfile.mkstemp()` + `os.replace()` — yari-yazili dosya kalmaz
5. SQLite DDL: `executescript()` ile trigger'li DDL (split(";") bozar)
6. Frozenset guard: gecersiz tur/eylem icin `frozenset` ile hizli kontrol
