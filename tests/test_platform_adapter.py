"""Test: reymen/platform_adapter.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestPlatform:
    def test_import(self):
        import reymen.platform_adapter

        assert reymen.platform_adapter is not None
