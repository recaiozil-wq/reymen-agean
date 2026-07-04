"""Test: reymen/guvenlik/ kalan moduller"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGuvenlik2:
    def test_docker_sandbox(self):
        import reymen.guvenlik.docker_sandbox

        assert reymen.guvenlik.docker_sandbox is not None

    def test_oauth_sistemi(self):
        import reymen.guvenlik.oauth_sistemi

        assert reymen.guvenlik.oauth_sistemi is not None

    def test_guardrails_module(self):
        import reymen.guvenlik.guardrails

        assert reymen.guvenlik.guardrails is not None
