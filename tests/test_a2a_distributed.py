"""Test: reymen/a2a_distributed.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestA2ADistributed:
    def test_import(self):
        import reymen.a2a_distributed as m

        assert m is not None
