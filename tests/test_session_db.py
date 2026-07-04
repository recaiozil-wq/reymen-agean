"""Test: session_db module"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSessionDB:
    def test_hafiza_import(self):
        import reymen.hafiza.session_db

        assert reymen.hafiza.session_db is not None

    def test_session_db_has_class(self):
        from reymen.hafiza.session_db import SessionDB, AdvancedSessionStorage

        assert SessionDB is not None
        assert AdvancedSessionStorage is not None

    def test_core_session_db_import(self):
        from src.core.session_db import SessionDB

        assert SessionDB is not None
