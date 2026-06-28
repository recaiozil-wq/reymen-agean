# -*- coding: utf-8 -*-
# SHIM — reymen/guvenlik/anayasa_denetci.py yönlendirir
from reymen.guvenlik.anayasa_denetci import *  # noqa: F401, F403

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.guvenlik.anayasa_denetci')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)

# Basit selamlama desenleri — LLM çağrısı gerekmez
_BASIT_DESENLER = frozenset([
    "merhaba", "selam", "hi", "hello", "hey", "teşekkür", "tesekkur",
    "tamam", "ok", "iyi", "güzel", "harika", "süper", "evet", "hayır",
])


def _basit_soru_mu_fn(hedef) -> bool:
    if not hedef:
        return False
    hedef_lower = str(hedef).lower().strip()
    if not hedef_lower:
        return False
    for desen in _BASIT_DESENLER:
        if hedef_lower.startswith(desen):
            return True
    return False


AnayasaDenetci._basit_soru_mu = staticmethod(_basit_soru_mu_fn)

# denetle: basit soru ise LLM çağrısını atla
_orijinal_denetle = AnayasaDenetci.denetle


def _denetle_patched(self, hedef: str, cevap: str, adim_gecmisi=None, revize_et: bool = True):
    if _basit_soru_mu_fn(hedef):
        return True, cevap
    return _orijinal_denetle(self, hedef, cevap, adim_gecmisi, revize_et)


AnayasaDenetci.denetle = _denetle_patched
