"""Test: delegation_manager."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestDelegasyon:
    def test_import(self):
        from reymen.core.delegation_manager import DelegationManager

        assert DelegationManager is not None

    def test_class(self):
        from reymen.core.delegation_manager import DelegationManager

        dm = DelegationManager()
        assert dm is not None
