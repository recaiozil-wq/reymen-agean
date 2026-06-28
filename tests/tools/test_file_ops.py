# -*- coding: utf-8 -*-
"""Test: file_ops.py — Dosya işlemleri."""

from unittest.mock import patch
from tools import file_ops


@patch("tools.file_ops._guvenli", lambda p: (True, ""))
@patch("tools.file_ops._yol_dogrula", lambda p: (True, p))
def test_yaz_oku(tmp_path):
    dosya = str(tmp_path / "test.txt")
    sonuc = file_ops.yaz(dosya, "merhaba dünya")
    assert "yazildi" in sonuc
    sonuc2 = file_ops.oku(dosya)
    assert "merhaba" in sonuc2


def test_yaz_no_filename():
    sonuc = file_ops.yaz("", "test")
    assert "gerekli" in sonuc


def test_oku_nonexistent():
    sonuc = file_ops.oku("/nonexistent_xyz.txt")
    assert "bulunamadi" in sonuc


def test_oku_no_filename():
    sonuc = file_ops.oku("")
    assert "gerekli" in sonuc


@patch("tools.file_ops._guvenli", lambda p: (True, ""))
@patch("tools.file_ops._yol_dogrula", lambda p: (True, p))
def test_yaz_newline_replace(tmp_path):
    dosya = str(tmp_path / "nl_test.txt")
    sonuc = file_ops.yaz(dosya, "satir1\\nsatir2")
    assert "yazildi" in sonuc
    with open(dosya, "r", encoding="utf-8") as f:
        icerik = f.read()
    assert "satir1" in icerik


def test_ping():
    assert file_ops.ping() is True
