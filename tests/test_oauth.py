"""Test: reymen/core/oauth_manager.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestOAuth:
    def test_import(self):
        import reymen.core.oauth_manager

        assert reymen.core.oauth_manager is not None

    def test_class(self):
        from reymen.core.oauth_manager import OAuthManager

        assert OAuthManager is not None
