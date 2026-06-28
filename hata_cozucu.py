# -*- coding: utf-8 -*-
# SHIM — reymen/cereyan/hata_cozucu.py yonlendirir
from reymen.cereyan.hata_cozucu import *  # noqa: F401, F403

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.cereyan.hata_cozucu')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
