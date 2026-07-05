# -*- coding: utf-8 -*-
"""Runtime calisma dizini yonetimi.

Hermes agent/runtime_cwd.py'den adapte edilmistir.
"""
from __future__ import annotations
import os
from pathlib import Path

def cwd_al() -> Path:
    return Path.cwd()

def cwd_ayarla(yol: Path) -> None:
    os.chdir(str(yol))
