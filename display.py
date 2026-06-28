# -*- coding: utf-8 -*-
# SHIM — reymen/sistem/display.py yonlendirir
from reymen.sistem.display import *  # noqa: F401, F403

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.sistem.display')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
