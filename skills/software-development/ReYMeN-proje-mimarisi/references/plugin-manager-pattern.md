---
skill_id: f53bec0036a7
usage_count: 1
last_used: 2026-06-16
---
# PluginManager Pattern

## Problem
ReYMeN Agent'te pluginler klasör tabanlıydı (her plugin bir alt dizin + `__init__.py`).
ReYMeN için daha hafif, tek dosyalı bir plugin sistemi gerekiyordu.

## Cozum: PluginManager + PluginManifest
`plugin_manager.py` — lazy loading, weakref, `run()` tabanlı.

## Dosya Yapisi
```
plugins/
  __init__.py          # Eski sistem (PluginYukleyici)
  ornek_tool.py        # Yeni sistem (PluginManager ile kesfedilir)
  ornek_plugin/        # Eski sistem (PluginYukleyici ile yuklenir)
    __init__.py
```

## Sinif Detaylari

### PluginManifest
- `name`: Plugin adi (dosya adi)
- `path`: Tam dosya yolu
- `_module_ref`: `weakref.ref` ile module referansi (GC dostu)
- `load()`: Modulu yukler, weakref'e kaydeder, modul doner
- `get_run()`: `load()` yapar, `run` attribute'unu dondurur

### PluginManager
- `_dir`: Plugin dizini (`Path`)
- `_registry`: `dict[str, PluginManifest]`
- `discover()`: `plugins/*.py` dosyalarini lazy tara (`_` ile baslayanlari atla)
- `get(name)`: Tek pluginin `run()` fonksiyonunu dondur
- `run(name, **kwargs)`: Plugin'i calistir, yoksa `KeyError`
- `list_plugins()`: Kesfedilen plugin isimlerini dondur
- `__del__()`: `_registry.clear()`

## Motor Entegrasyonu
`motor.py`'de `calistir()` metodu su siralamayla calisir:
1. **ToolRegistry** (`tools/` klasorundeki araclar)
2. **PluginManager** (`plugins/*.py` dosyalari)
3. **Fallback if/else** (eski motor.py if/else zinciri)

```python
# motor.py'de entegrasyon:
try:
    from plugin_manager import PluginManager as _PluginManager
    _PLUGIN_MGR = _PluginManager(str(ROOT / "plugins"))
except ImportError:
    _PLUGIN_MGR = None

# calistir() icinde:
# 1. ToolRegistry ile dene
if _REGISTRY:
    sonuc = _REGISTRY.calistir(arac, *params)
    if "Bilinmeyen arac" not in sonuc:
        return sonuc

# 2. PluginManager ile dene
if _PLUGIN_MGR and "Bilinmeyen arac" in sonuc:
    try:
        plugin_sonuc = _PLUGIN_MGR.run(arac.lower(), *params)
        return str(plugin_sonuc)
    except KeyError:
        pass  # Plugin'de de yok, fallback'e gec

# 3. Fallback if/else
sonuc = self._fallback_calistir(arac, params)
```

## Test Sonuclari
| Test | Sonuc |
|------|-------|
| `list_plugins()` → `['ornek_tool']` | ✅ |
| `run('ornek_tool', target='ReYMeN')` → `Hello, ReYMeN!` | ✅ |
| Olmayan plugin → `KeyError` | ✅ |
| Weakref (cift cagri) → calisiyor | ✅ |
| Motor entegrasyonu → PluginManager yuklu | ✅ |
| Derleme (py_compile) → sifir hata | ✅ |
