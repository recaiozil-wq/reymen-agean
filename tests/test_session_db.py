"""Test: session_db module"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSessionDB:
    def test_core_import(self):
        import reymen.core.session_db

        assert reymen.core.session_db is not None

    def test_hafiza_import(self):
        import reymen.hafiza.session_db

        assert reymen.hafiza.session_db is not None
