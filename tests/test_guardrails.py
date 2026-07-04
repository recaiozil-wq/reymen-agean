"""Test: reymen/guvenlik/ modulleri"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestGuvenlik:
    def test_guardrails_module(self):
        import reymen.guvenlik.guardrails

        assert reymen.guvenlik.guardrails is not None

    def test_file_safety(self):
        from reymen.guvenlik.file_safety import guvenli_mi

        assert callable(guvenli_mi)

    def test_security_engine(self):
        from reymen.guvenlik.security_engine import SecurityEngine

        assert SecurityEngine is not None

    def test_threat_detector(self):
        from reymen.guvenlik.threat_patterns import ThreatDetector

        assert ThreatDetector is not None

    def test_tool_guardrails(self):
        from reymen.guvenlik.tool_guardrails import ToolGuardrails

        assert ToolGuardrails is not None

    def test_anayasa_denetci(self):
        from reymen.guvenlik.anayasa_denetci import AnayasaDenetci

        assert AnayasaDenetci is not None
