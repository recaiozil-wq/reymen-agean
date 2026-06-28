#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_browser_tool.py — Browser tool testleri."""

import sys
sys.path.insert(0, ".")

from tools.browser_tool import run, motor_kaydet


class TestBrowser:
    def test_navigate(self):
        r = run(islem="navigate", url="https://example.com")
        assert "[Browser]" in r

    def test_navigate_no_url(self):
        r = run(islem="navigate")
        assert "URL gerekli" in r

    def test_click(self):
        r = run(islem="click", ref="@e5")
        assert "[Browser]" in r

    def test_click_no_ref(self):
        r = run(islem="click")
        assert "ref gerekli" in r

    def test_type(self):
        r = run(islem="type", ref="@e3", text="Merhaba")
        assert "[Browser]" in r

    def test_scroll(self):
        r = run(islem="scroll", yon="down")
        assert "[Browser]" in r

    def test_snapshot(self):
        r = run(islem="snapshot")
        assert "[Browser]" in r

    def test_vision(self):
        r = run(islem="vision")
        assert "[Browser]" in r

    def test_back(self):
        r = run(islem="back")
        assert "[Browser]" in r

    def test_status(self):
        r = run(islem="status")
        assert "hazir" in r

    def test_no_islem(self):
        r = run()
        assert "gerekli" in r

    def test_bilinmeyen(self):
        r = run(islem="olmayan")
        assert "Bilinmeyen" in r

    def test_motor_kaydet(self):
        class FakeMotor:
            def _plugin_arac_kaydet(self, *a):
                self.kaydedildi = a
        m = FakeMotor()
        motor_kaydet(m)
        assert hasattr(m, "kaydedildi")
