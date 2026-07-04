"""Test: ogrenme."""

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class TestOgrenme:
    def test_imza_uret(self):
        from reymen.core.ogrenme import imza_uret

        imza = imza_uret(ValueError("test"))
        assert isinstance(imza, str) and len(imza) > 0

    def test_cozum_bul_bos(self):
        from reymen.core.ogrenme import cozum_bul

        assert cozum_bul("olmayan_imza_123") is None

    def test_import(self):
        from reymen.core.ogrenme import OgrenmeDongusu

        assert OgrenmeDongusu is not None
