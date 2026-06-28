#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_toolset_manager.py — ToolsetManager testleri."""

import sys
sys.path.insert(0, ".")

from agent.toolset_manager import ToolsetManager, toolset_manager


class TestToolsetInit:
    def test_init_bos(self):
        ts = ToolsetManager({})
        assert len(ts.listele()) >= 9  # 9 varsayilan toolset
        assert ts.ping() is True

    def test_init_ozel(self):
        ts = ToolsetManager({"toolsets": {"enabled": ["terminal", "file"]}})
        assert ts.aktif_toolsets() == ["file", "terminal"]

    def test_singleton(self):
        ts1 = toolset_manager({"toolsets": {}})
        ts2 = toolset_manager()
        assert ts1 is ts2


class TestToolsetIslem:
    def test_listele(self):
        ts = ToolsetManager({})
        liste = ts.listele()
        assert any(t["ad"] == "terminal" for t in liste)
        assert any(t["ad"] == "web" for t in liste)

    def test_aktif_toolsets(self):
        ts = ToolsetManager({})
        aktif = ts.aktif_toolsets()
        assert "terminal" in aktif
        assert len(aktif) >= 9

    def test_etkinlestir_ve_kapat(self):
        ts = ToolsetManager({"toolsets": {"enabled": []}})
        assert ts.aktif_toolsets() == []
        ts.etkinlestir("terminal")
        assert "terminal" in ts.aktif_toolsets()
        ts.devre_disi_birak("terminal")
        assert "terminal" not in ts.aktif_toolsets()

    def test_etkinlestir_olmayan(self):
        ts = ToolsetManager({})
        r = ts.etkinlestir("olmayan")
        assert "bulunamadi" in r

    def test_aktif_araclar(self):
        ts = ToolsetManager({})
        araclar = ts.aktif_araclar()
        assert "terminal" in araclar
        assert "web_search" in araclar or "web" in araclar


class TestToolsetKomut:
    def test_komut_list(self):
        ts = ToolsetManager({})
        r = ts.komut_islem("")
        assert "Toolsets" in r
        assert "terminal" in r

    def test_komut_ac(self):
        ts = ToolsetManager({"toolsets": {"enabled": []}})
        r = ts.komut_islem("ac terminal")
        assert "etkinlestirildi" in r

    def test_komut_kapat(self):
        ts = ToolsetManager({})
        r = ts.komut_islem("kapat terminal")
        assert "devre disi" in r

    def test_komut_bilinmeyen(self):
        ts = ToolsetManager({})
        r = ts.komut_islem("olmayan")
        assert "Bilinmeyen" in r
