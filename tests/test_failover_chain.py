"""Test: reymen/ag/failover_chain.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestFailover:
    def test_import(self):
        import reymen.ag.failover_chain as fc

        assert fc is not None
