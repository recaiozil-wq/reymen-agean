---
skill_id: 1df8f3fcc855
usage_count: 1
last_used: 2026-06-16
---
# ToolRegistry Cozulemeyen Moduller

## Hata Semptomu

```text
FAILED tests/test_tools.py::TestToolTemplates::test_tool_module_callable_exists[file_ops]
FAILED tests/test_tools.py::TestToolTemplates::test_tool_module_callable_exists[screen]
...
AssertionError: Tool file_ops cozulmeli
assert None is not None
```

Ayni hata 2 test metodu icin N tane tool adiyla tekrarlanir:
- `test_tool_module_callable_exists[tool_adi]`
- `test_dispatcher_can_resolve_tool[tool_adi]`

## Kok Neden

`ToolRegistry._yukle()` (tool_registry.py) sadece **`run()` fonksiyonu olan** modulleri `_tools` sozlugune yukler:

```python
if hasattr(mod, "run"):
    self._tools[f.stem.upper()] = getattr(mod, "run")
```

Bazi tool modulleri ozel fonksiyon adlari kullanir (`oku()`/`yaz()`, `ekran_oku()`/`tikla()`, `sayfa_ac()`), `run()` tanimlamaz. Bu moduller `_tools`'a eklenmez.

`resolve(ad)` cagrildiginda:
1. `ad.upper()` `_tools`'ta yok (yuklenmemis)
2. `_aliases`'ta da yok (alias'lar eski stil buyuk harfli adlar, modul adi degil)
3. → `None` doner

## Tespit

Hangi modullerde `run()` olmadigini bul:

```bash
python -c "
from pathlib import Path; import importlib
for f in sorted(Path('tools').glob('*.py')):
    if f.name.startswith('_'): continue
    mod = importlib.import_module('tools.' + f.stem)
    funcs = [n for n in dir(mod) if callable(getattr(mod,n)) and not n.startswith('_')]
    if not hasattr(mod, 'run'):
        print(f'{f.stem}: NO run(), funcs={funcs}')
"
```

## Fix Deseni

`resolve()` metoduna 3. bir kontrol yolu ekle: `_tools` ve `_aliases`'tan sonra, dogrudan `tools/{modul_adi}.py` dosyasini ara. Varsa modulu import et ve en uygun callable'i bul.

### Yardimci Metod

```python
def _moduldeki_ilk_callable(self, mod_name: str) -> str | None:
    """tools/ modulundeki en uygun callable'i bul (ping > run > ilk public fonk)."""
    try:
        mod = importlib.import_module(f"tools.{mod_name}")
    except Exception:
        return None
    for candidate in ("ping", "run"):
        if hasattr(mod, candidate):
            return candidate
    funcs = [
        n for n in dir(mod)
        if callable(getattr(mod, n)) and not n.startswith("_")
    ]
    return funcs[0] if funcs else None
```

### resolve() Fallback

```python
def resolve(self, ad: str) -> dict[str, str] | None:
    # ... mevcut _tools ve _aliases kontrolleri ...
    
    # Modul adi direkt kontrol
    mod_name = ad.strip().lower()
    mod_path = TOOLS_DIR / f"{mod_name}.py"
    if mod_path.exists():
        callable_name = self._moduldeki_ilk_callable(mod_name)
        if callable_name:
            return {"module": mod_name, "callable": callable_name}
    
    return None
```

## Onaylama

```bash
python -m pytest tests/test_tools.py -q
# Basta: N passed, 26 failed
# Fix sonrasi: 233 passed (hepsi yesil)
```

## Yaygin Tool Modulleri ve Callable'lari

| Modul | Fonksiyonlar | run() var mi? |
|-------|--------------|:---:|
| file_ops | `oku()`, `yaz()`, `ping()` | ✗ |
| screen | `ekran_oku()`, `tikla()`, `nisan_ciz()`, `ping()` | ✗ |
| browser | `sayfa_ac()`, `ping()` | ✗ |
| web_search | `ara()`, `ping()` | ✗ |
| macro | `oynat()`, `ping()` | ✗ |
| image_generation_tool | `resim_uret()`, `gorsel_analiz_et()` | ✗ |
| memory_tool | `memory_ara()`, `memory_oku()`, `memory_yaz()` | ✗ |
| mcp_tool | `mcp_tool_cagir()`, `mcp_tool_listele()` | ✗ |
| tts_tool | `metni_sese_cevir()` | ✗ |
| transcription_tools | `sesi_metne_cevir()` | ✗ |
| send_message_tool | `mesaj_gonder()`, `telegram_gonder()`, `terminal_gonder()` | ✗ |
| video_generation_tool | `video_uret()` | ✗ |
| x_search_tool | `x_ara()` | ✗ |

## Pitfall

- `_yukle()` sadece `run()` kontrolu yapar. `ping()` olan moduller de yuklenmez — `ping()` fallback'i sadece `resolve()` seviyesinde calisir.
- `calistir()` metodu `self._tools[ad](*args, **kwargs)` ile dogrudan cagiri yapar, alias sistemini kullanmaz. Alias uzerinden calistirma `calistir()` icinde ayri bir dala gider.
- Python import cach'lidir, `importlib.import_module()` ikinci cagrida tekrar yuklemez — hiz sorunu olmaz.
