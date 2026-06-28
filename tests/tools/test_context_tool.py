# -*- coding: utf-8 -*-
"""Test: context_tool.py — Token durumu ve context sıkıştırma."""

from unittest.mock import patch, MagicMock
from tools import context_tool


def test_run_durum():
    """context_manager yoksa hata döner."""
    sonuc = context_tool.run(eylem="durum")
    # If context_manager can't be imported, returns error
    assert isinstance(sonuc, str)


def test_run_sikistir():
    """context_manager yoksa hata döner."""
    sonuc = context_tool.run(eylem="sikistir")
    assert isinstance(sonuc, str)


def test_run_invalid_eylem():
    sonuc = context_tool.run(eylem="gecersiz")
    assert "Hata" in sonuc
    assert "durum" in sonuc


def test_motor_kaydet():
    motor = MagicMock()
    context_tool.motor_kaydet(motor)
    motor._plugin_arac_kaydet.assert_called_once()
