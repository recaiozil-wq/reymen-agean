# -*- coding: utf-8 -*-
"""
apps/ — ReYMeN Hazir Uygulama Moduller.

Her modul bagimsiz calisabilir ve ajan tarafindan da cagrilabilir.

Moduller:
  web_arastirma   — URL + DuckDuckGo arama + ozet
  dosya_duzenleyici — Dosya okuma/yazma/arama/yedekleme
  kod_analizi     — Python kod metrik ve hata analizi
  not_defteri     — Markdown not alma ve arama
"""


__all__ = ['Any', 'Path', 'import_module', 'listele', 'uygulama_cagir']
from importlib import import_module
from pathlib import Path
from typing import Any

_MODULLER = {
    "web_arastirma":    "apps.web_arastirma",
    "dosya":            "apps.dosya_duzenleyici",
    "kod":              "apps.kod_analizi",
    "not":              "apps.not_defteri",
}


def uygulama_cagir(ad: str, metot: str, **kwargs) -> Any:
    """Ortak uygulama cagiri — ajan motorundan kullanilir."""
    modul_yolu = _MODULLER.get(ad)
    if not modul_yolu:
        return {"hata": f"Bilinmeyen uygulama: {ad}. Mevcut: {list(_MODULLER)}"}
    try:
        mod = import_module(modul_yolu)
        fn = getattr(mod, metot, None)
        if fn is None:
            return {"hata": f"{modul_yolu}.{metot} bulunamadi"}
        return fn(**kwargs)
    except Exception as e:
        return {"hata": str(e)}


def listele() -> list[str]:
    return list(_MODULLER)
