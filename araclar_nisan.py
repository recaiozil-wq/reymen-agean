# -*- coding: utf-8 -*-
# SHIM — reymen/arac/araclar_nisan.py yonlendirir
from reymen.arac.araclar_nisan import *  # noqa: F401, F403

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.arac.araclar_nisan')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
