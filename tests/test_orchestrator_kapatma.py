"""Test: orchestrator."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestOrchestrator:
    def test_functionlar_import(self):
        from reymen.core.orchestrator import run_script, solve_all, coz_hata

        assert run_script is not None

    def test_run_script_basarisiz(self):
        from reymen.core.orchestrator import run_script

        ok, out = run_script("/var/olmayan/dosya.py")
        assert ok is False

    def test_coz_hata(self):
        from reymen.core.orchestrator import coz_hata

        r = coz_hata("ModuleNotFoundError: No module named 'x'", ad="test")
        assert isinstance(r, str)
