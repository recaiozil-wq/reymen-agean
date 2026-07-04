"""Test: reymen/guvenlik/docker_sandbox.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestDockerSandbox:
    def test_import(self):
        import reymen.guvenlik.docker_sandbox as m

        assert m is not None
