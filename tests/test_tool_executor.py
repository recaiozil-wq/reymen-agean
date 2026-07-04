"""Test: reymen/arac/tool_executor.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestToolExec:
    def test_import(self):
        import reymen.arac.tool_executor

        assert reymen.arac.tool_executor is not None
