"""Test: reymen/sistem/config_loader.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestConfig:
    def test_module_import(self):
        import reymen.sistem.config_loader

        assert reymen.sistem.config_loader is not None
