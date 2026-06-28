# -*- coding: utf-8 -*-
"""Test: screen.py — Ekran okuma aracı."""
from tools import screen


def test_ping():
    """ping bool döndürür."""
    sonuc = screen.ping()
    assert isinstance(sonuc, bool)


def test_ekran_oku():
    """ekran_oku çalışır."""
    sonuc = screen.ekran_oku()
    assert sonuc is not None
    assert isinstance(sonuc, str)


def test_tikla():
    """tikla çalışır."""
    sonuc = screen.tikla("test")
    assert sonuc is not None


def test_nisan_ciz():
    """nisan_ciz çalışır."""
    sonuc = screen.nisan_ciz("test")
    assert sonuc is not None
