---
skill_id: 7408213d4934
usage_count: 1
last_used: 2026-06-16
---
# Tool Olusturma Workflow'u (16 Haziran 2026)

Bu belge, ReYMeN projesine yeni bir tool eklemek icin
kullanilmasi gereken adimlari ve kullanicinin tercihlerini icerir.

## Adim 1: Tool Dosyasini Olustur

`tools/` klasorunde yeni bir `.py` dosyasi olustur.

Her tool dosyasi **iki fonksiyon** icermelidir:

```python
# -*- coding: utf-8 -*-
"""tool_adi.py — Kisacik aciklama."""

def run(param1: str = "varsayilan", param2: str = "") -> str:
    """Kisa aciklama."""
    # ... mantik ...
    return "[Tamam] Islem basarili"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("TOOL_ADI", run, "Kisa aciklama")
```

### Kurallar
- `run(**kwargs) -> str` — tum tool'lar ayni imzayi kullanir
- `motor_kaydet(motor)` — motor'a kayit icin zorunlu
- `__file__.resolve()` ile yol sabitle (guvenlik)
- Bos metin/dosya kontrolleri en basta yapilir
- try/except ile hata yonetimi
- Temp dosyalari temizlenir (unlink/missing_ok)
- Docstring her fonksiyonda

## Adim 2: motor.py'ye Kayit Ekle

`motor.py` icinde `_plugin_moduller_yukle()` metodunda,
modul listesine yeni satir ekle:

```python
# tools.tool_adi
"tools.tool_adi",
```

Ekleme sirasi: Batch 9 ve 10 arasina, alfabetik degil,
kronolojik (en son eklenen en alta).

## Adim 4: Gelismis Pattern'ler

### Lazy Import (session_search_tool ornegi)
Modul import sirasinda baglanmayi onlemek icin:

```python
_STORE: Any = None  # Lazy

def _get_store():
    global _STORE
    if _STORE is None:
        from session_db import AdvancedSessionStorage
        _STORE = AdvancedSessionStorage(str(_DB_PATH))
    return _STORE
```

### Parametre Guvencesi
```python
def _parse_limit(deger, varsayilan: int = 5) -> int:
    try:
        return max(1, min(int(deger), 20))
    except (TypeError, ValueError):
        return varsayilan
```

### Coklu Format Destegi (dict veya tuple)
```python
def _satir(kayit, indeks) -> str:
    if isinstance(kayit, dict):
        hedef = str(kayit.get("hedef", "?"))[:80]
    elif isinstance(kayit, (list, tuple)) and len(kayit) >= 3:
        hedef = str(kayit[0])[:80]
    else:
        return f"  {indeks}. {str(kayit)[:200]}"
```

```bash
python -m py_compile tools/tool_adi.py
python -c "from tools.tool_adi import run; print(run())"
```

## Kullanici Tercihleri (Kritik)

1. **Kodu kullanici verir** — kullanici tool kodunu saglar,
   ben sadece dosyaya yazar, motor'a kaydeder ve test ederim.
   Kendi kodumu yazip "alternatif sunma" — kullanicinin kodunu
   aynen uygula.

2. **Her adimda dogrulama** — dosya olusturulduktan sonra
   `py_compile` ile derleme kontrolu, sonra `python -c` ile
   fonksiyonel test yapilir.

3. **Once goster, sonra uygula** — kullanici "bana goster"
   derse, kodu once goster, onay al, sonra uygula.

4. **Tool adi buyuk harf** — `_plugin_arac_kaydet("TOOL_ADI", ...)`
   ile kaydedilir, LLM ciktisinda da buyuk harfle cagrilir.

5. **sistem_talimati.py guncellemesi** — yeni tool'un nasil
   kullanilacagi sistem_talimati.py'deki arac listesine
   aciklama satiri olarak eklenir.
