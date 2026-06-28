# -*- coding: utf-8 -*-
"""Test: path_security.py — Yol güvenliği sarmalayıcısı."""

from tools import path_security


def test_run_dogrula_no_yol():
    sonuc = path_security.run(islem="dogrula")
    assert "Hata" in sonuc
    assert "yol" in sonuc


def test_run_symlink_no_yol():
    sonuc = path_security.run(islem="symlink_kontrol")
    assert "Hata" in sonuc
    assert "yol" in sonuc


def test_run_invalid_islem():
    sonuc = path_security.run(islem="gecersiz", yol="/tmp")
    assert "Hata" in sonuc


def test_run_dogrula_valid(tmp_path):
    dosya = tmp_path / "test.txt"
    dosya.write_text("test")
    sonuc = path_security.run(islem="dogrula", yol=str(dosya))
    assert "GUVENLI" in sonuc or "ENGELLENDI" in sonuc


def test_run_symlink(tmp_path):
    dosya = tmp_path / "test.txt"
    dosya.write_text("test")
    sonuc = path_security.run(islem="symlink_kontrol", yol=str(dosya))
    assert "GUVENLI" in sonuc or "RISKLI" in sonuc
