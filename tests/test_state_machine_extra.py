"""Test: reymen/sistem/ReYMeN_state.py ve state modulleri"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestState:
    def test_import(self):
        import reymen.sistem.ReYMeN_state as m

        assert m is not None
