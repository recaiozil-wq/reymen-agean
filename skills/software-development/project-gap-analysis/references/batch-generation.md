---
skill_id: 6c8bb249bff9
usage_count: 1
last_used: 2026-06-16
---
# Batch Generation: Hizli Kod Uretim Metodolojisi

Gap analizi sonrasi eksik dosyalari hizla uretmek icin kullanilir.
Hedef: her batch'te 5-6 dosyayi paralel yaz, import testi yap, tekrarla.

## Adim 1: Batch Gruplari Olustur

Dosyalari once bagimsizliklarina gore grupla:

| Grup | Tur | Ornekler | Batch Boyutu |
|------|-----|----------|--------------|
| A | Hicbir seye bagimli degil | context_references.py, trajectory.py | 5-6 |
| B | Ayni klasorde | tools/*.py | 4-6 |
| C | Birbirine referans veren | gateway/*.py | 3-4 |
| D | Dis API gerektiren | bedrock_adapter.py, codex_runtime.py | 2-3 |

## Adim 2: Batch'leri Calistir

Her batch icin:
1. Tum dosyalari `write_file` ile paralel yaz
2. Tek `python -c "import A; import B; ..."` ile import testi yap
3. Hata varsa duzelt, yoksa sonraki batch'e gec

**Kritik:** Bir batch'te hata varsa sonraki batch'e gecme. 0 hata garantisi olmali.

## Adim 3: todo ile Takip

```
todos = [
  {"id": "1", "content": "batch A: bagimsiz dosyalar", "status": "in_progress"},
  {"id": "2", "content": "batch B: tools/*", "status": "pending"},
  ...
]
```

Her batch tamamlaninca `completed` yap, ilerleme tablosu goster.

## Optimal Batch Buyuklugu

- **5-6 dosya**: ideal (parallel write limitine takilmadan maksimum)
- **1 import testi / batch**: ideal (tek seferde 5-6 modulu kontrol)
- **14 batch / 28 dosya**: bu oturumdaki gercek performans = ~2 saat

## Uyari: Circular Import

Gateway platformlarinda `from . import __init__` yapma — `method-wrapper` hatasi alirsin.
Cozum: platform dosyalarinda sadece fonksiyon tanimla, kaydi `__init__.py`'de `importlib.import_module` ile yap:

```python
# __init__.py'de:
import importlib
mod = importlib.import_module("gateway.platforms.discord")
kaydet("discord", getattr(mod, "baslat"), getattr(mod, "durdur"), getattr(mod, "mesaj_gonder"))
```

## ACP (Agent Communication Protocol) Minimal Yaklasim

ACP buyuk bir protokoldur (ReYMeN'te 6+ dosya). ReYMeN icin minimal versiyon yeterlidir:
- `server.py`: TCP socket + stdio, JSON-RPC 2.0, tool kaydetme
- `client.py`: TCP + stdio istemci, ping + tool_call
- `auth.py`: HMAC + timestamp dogrulama
- `agent.json`: ajan karti

Bu 4 dosya ~30 satir/server.py, ~40 satir/client.py, ~20 satir/auth.py ile calisir.
