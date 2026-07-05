# -*- coding: utf-8 -*-
"""Process baslangic ayarlari.

Hermes agent/process_bootstrap.py'den adapte edilmistir.
"""
from __future__ import annotations
import os
import sys

def bootstrap() -> None:
    """Process baslangic ayarlarini yap."""
    sys.dont_write_bytecode = True
    os.environ.setdefault("PYTHONUNBUFFERED", "1")
