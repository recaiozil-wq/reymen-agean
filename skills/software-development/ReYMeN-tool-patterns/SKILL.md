---
name: ReYMeN-tool-patterns
category: software-development
version: 1.0.0
description: ReYMeN projesinde tool gelistirme pattern'leri ve kritik kod yapilari
tags: [skill, hermes, ReYMeN, patterns, tools]
---

# ReYMeN-tool-patterns

ReYMeN projesine yeni tool eklerken kullanilacak pattern'ler.

## Ozet Tablo

| # | Dosya | Kritik Pattern |
|---|-------|----------------|
| 1 | session_search_tool.py | Lazy store + _parse_limit + dict/tuple kayit guard |
| 2 | execute_code_tool.py | Lazy lab + TimeoutError/MemoryError ayrimi |
| 3 | delegate_task_tool.py | sys.executable + returncode kontrolu + json_cikti flag |
| 4 | vision_tool.py | mkstemp + lazy PIL + ayri exception tipi |
| 5 | discord.py | Interface uyumu + mesaj_akisi generator |
| 6 | test_tools.py | monkeypatch + network mock + her tool icin 3-4 case |
| 7 | context_tool.py | Lazy ctx + method adi fallback chain + TypeError retry |
| 8 | memory_providers/base.py | ABC BellekSaglayici interface — kaydet/oku/ara/sil/durum |
| 9 | memory_providers/file_provider.py | Atomic write (temp+rename) + JSON bozuk dosya recovery |
| 10 | memory_providers/chromadb_provider.py | upsert duplicate-safe + n_results ≤ count() guard |
| 11 | memory_providers/sqlite_provider.py | FTS5 check via compileoption + executescript DDL + LIKE fallback |
| 12 | memory_providers/redis_provider.py | scan_iter lazy iterator + namespace index (sadd) + decode_responses |
| 13 | memory_providers/memory_bridge.py | threading.Lock singleton + frozenset validation + deger=None default |

## Standart Tool Sablonu

```python
# -*- coding: utf-8 -*-
"""ornek_tool.py — Aciklama."""

from __future__ import annotations
from typing import Any

_VAR: Any = None  # Lazy

def _get_var():
    global _VAR
    if _VAR is None:
        from module import Class  # gec import
        _VAR = Class()
    return _VAR

def run(param: str = "") -> str:
    if not param:
        return "[Hata]: param parametresi gerekli."
    try:
        obj = _get_var()
        return str(obj.islem(param))
    except Exception as e:
        return f"[Hata]: {e}"

def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("ORNEK", run, "Aciklama")
```

## Motor'a Kayit

Her yeni tool `motor.py`'de `_plugin_moduller_yukle()` listesine eklenir:

```python
"tools.ornek_tool",
```

## Pitfall'lar

| Hata | Cozum |
|------|-------|
| `liste` eylemi → `store.son_oturumlar()` bulunamadi | `dir(store)` ile gercek method adlarini kontrol et, uymuyorsa fallback mesaj goster |
| SQLite DDL → `incomplete input` | Trigger'lar noktali virgul icerdigi icin `split(";")` bozar. **`executescript()`** ile tek seferde gonder |
| FTS5 kontrolu → `SELECT fts5(?)` hata veriyor | `SELECT sqlite_compileoption_get(0)` ile "FTS5" string'i ara |
| `context_tool.py` → `compress()` missing 1 argument | `AdvancedContextCompressor.compress(mesajlar)` gerektirir — tool disindan cagrilamaz, sadece ReAct dongusu icinde calisir |
| Docker `from_env()` hatasi | `import docker` basarili ama daemon calismiyor. `ping()` ile ek kontrol ekle, fallback local subprocess'e dus |

```bash
python -m py_compile tools/ornek_tool.py
python -m pytest tests/ -v
```
