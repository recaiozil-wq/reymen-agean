"""Test: reymen/ag/delegation.py + kopru"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestDelegasyon:
    def test_delegation_import(self):
        import reymen.ag.delegation

        assert reymen.ag.delegation is not None
