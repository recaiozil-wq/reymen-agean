"""Test: reymen/core/guardrails_manager.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGuardrails2:
    def test_import(self):
        import reymen.core.guardrails_manager

        assert reymen.core.guardrails_manager is not None
