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

    def test_hallucination_filtresi(self):
        from reymen.guvenlik.guardrails import HallucinationFiltresi
        hf = HallucinationFiltresi()
        sonuc = hf.filtrele("test mesaji")
        assert sonuc is not None

    def test_hitl_sikistirici(self):
        from reymen.guvenlik.guardrails import HITLSikistirici
        hitl = HITLSikistirici()
        assert hitl is not None

    def test_docker_sandbox_import(self):
        import reymen.guvenlik.docker_sandbox as m
        assert m is not None

    def test_oauth_import(self):
        import reymen.guvenlik.oauth_sistemi as m
        assert m is not None

    def test_file_safety_import(self):
        import reymen.guvenlik.file_safety as m
        assert m is not None

    def test_url_safety_import(self):
        import reymen.guvenlik.url_safety as m
        assert m is not None

    def test_threat_patterns_import(self):
        import reymen.guvenlik.threat_patterns as m
        assert m is not None

    def test_redact_import(self):
        import reymen.guvenlik.redact as m
        assert m is not None

    def test_message_sanitization_import(self):
        import reymen.guvenlik.message_sanitization as m
        assert m is not None
