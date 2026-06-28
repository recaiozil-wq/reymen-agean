---
skill_id: 5ddaca73cb8c
usage_count: 1
last_used: 2026-06-16
---
# Batch Dosya Olusturma Sablonu

## Dosya Basligi (her dosyada zorunlu)

```python
# -*- coding: utf-8 -*-
"""dosya_adi.py — Kisacik aciklama (1 satir).

Detayli aciklama (2-5 satir).
Ne ise yarar, nasil kullanilir, hangi durumlarda cagrilir.

Kullanim:
    from dosya_adi import Sinif
    s = Sinif()
    s.metod()
"""
```

## Sinif Yapisi

```python
class SinifAdi:
    """Sinif aciklamasi."""

    def __init__(self, parametre: str = ""):
        self.parametre = parametre

    def metod(self, girdi: str) -> str:
        """Metod aciklamasi.

        Args:
            girdi: Aciklama

        Returns:
            Donus degeri
        """
        try:
            return f"[Sonuc]: {girdi}"
        except Exception as e:
            return f"[Hata]: {e}"
```

## Test Blogu (her dosyada zorunlu)

```python
if __name__ == "__main__":
    s = SinifAdi()
    print(s.metod("test"))
```

## Batch Dogrulama (her batch sonrasi)

```python
import sys; sys.path.insert(0, '.')
mods = ['dosya1', 'dosya2', 'dosya3']
ok = 0
for m in mods:
    try:
        __import__(m)
        print(f'  {m}: OK')
        ok += 1
    except Exception as e:
        print(f'  {m}: HATA {str(e)[:60]}')
print(f'\n{ok}/{len(mods)} basarili')
```

## Graceful Degrade Pattern (opsiyonel kutuphaneler icin)

```python
try:
    import kutuphane
    KUTUPHANE_VAR = True
except ImportError:
    KUTUPHANE_VAR = False

def fonksiyon():
    if not KUTUPHANE_VAR:
        return "[Modul]: kutuphane kurulu degil (pip install kutuphane)"
    ...
```
