# -*- coding: utf-8 -*-
# SHIM — reymen/guvenlik/threat_patterns.py yönlendirir
from reymen.guvenlik.threat_patterns import *  # noqa: F401, F403


# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.guvenlik.threat_patterns')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
