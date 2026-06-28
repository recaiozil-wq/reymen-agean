# -*- coding: utf-8 -*-
# SHIM — reymen/windows/tor_otomasyonu.py yonlendirir
from reymen.windows.tor_otomasyonu import *  # noqa: F401, F403

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.windows.tor_otomasyonu')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
