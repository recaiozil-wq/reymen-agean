# -*- coding: utf-8 -*-
# SHIM — reymen/cereyan/closed_learning_loop.py yonlendirir
from reymen.cereyan.closed_learning_loop import *  # noqa: F401, F403

# Private isimleri de disıaçar (testler için)
import importlib as _imp, sys as _sys
_src = _imp.import_module('reymen.cereyan.closed_learning_loop')
_sys.modules[__name__].__dict__.update(
    {k: v for k, v in vars(_src).items() if k.startswith('_') and not k.startswith('__')}
)
