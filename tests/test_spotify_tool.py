#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_spotify_tool.py — Spotify tool testleri."""

import sys
sys.path.insert(0, ".")

from tools.spotify_tool import run


class TestSpotify:
    def test_cal(self):
        r = run(islem="cal")
        assert "[Spotify]" in r

    def test_durdur(self):
        r = run(islem="durdur")
        assert "[Spotify]" in r

    def test_ara(self):
        r = run(islem="ara", sorgu="pink floyd")
        assert "[Spotify]" in r

    def test_sonraki(self):
        r = run(islem="sonraki")
        assert "[Spotify]" in r

    def test_onceki(self):
        r = run(islem="onceki")
        assert "[Spotify]" in r

    def test_durum(self):
        r = run(islem="durum")
        assert "[Spotify]" in r

    def test_no_islem(self):
        r = run()
        assert "gerekli" in r

    def test_bilinmeyen(self):
        r = run(islem="olmayan")
        assert "Bilinmeyen" in r
