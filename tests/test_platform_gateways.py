"""Test: reymen/ag/platform_gateways.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestPlatformGateways:
    def test_import(self):
        import reymen.ag.platform_gateways as m

        assert m is not None

    def test_siniflar(self):
        from reymen.ag.platform_gateways import (
            TelegramGateway,
            CLIGateway,
            DiscordGateway,
        )

        assert TelegramGateway is not None
