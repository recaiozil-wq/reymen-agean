"""Test: reymen/a2a_transport.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestA2ATransport:
    def test_import(self):
        import reymen.a2a_transport as m

        assert m is not None
