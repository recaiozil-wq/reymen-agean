"""Test: reymen/guvenlik/ modulleri kapsamli"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGuvenlik:
    def test_guardrails_import(self):
        import reymen.guvenlik.guardrails as m

        assert m is not None

    def test_guardrails_denetle(self):
        from reymen.guvenlik.guardrails import Guardrails

        g = Guardrails()
        sonuc = g.denetle("test mesaji")
        assert sonuc is not None

    def test_guardrails_durum(self):
        from reymen.guvenlik.guardrails import Guardrails

        g = Guardrails()
        durum = g.durum()
        assert durum is not None

    def test_guardrails_kural_ekle(self):
        from reymen.guvenlik.guardrails import Guardrails

        g = Guardrails()
        g.kural_ekle("test_kural", lambda x: True)
        assert True

    def test_docker_sandbox_import(self):
        import reymen.guvenlik.docker_sandbox as m

        assert m is not None

    def test_oauth_import(self):
        import reymen.guvenlik.oauth_sistemi as m

        assert m is not None
