---
skill_id: 367d9ba442c8
usage_count: 1
last_used: 2026-06-16
---
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
