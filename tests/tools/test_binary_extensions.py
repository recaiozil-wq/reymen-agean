# -*- coding: utf-8 -*-
"""Test: binary_extensions.py — Binary uzantı tespiti."""

from tools import binary_extensions


def test_run_kontrol_binary():
    sonuc = binary_extensions.run(islem="kontrol", dosya_adi="test.exe")
    assert "Binary" in sonuc


def test_run_kontrol_text():
    sonuc = binary_extensions.run(islem="kontrol", dosya_adi="test.txt")
    assert "Metin" in sonuc


def test_run_kontrol_no_filename():
    sonuc = binary_extensions.run(islem="kontrol")
    assert "Hata" in sonuc
    assert "dosya_adi" in sonuc


def test_run_liste():
    sonuc = binary_extensions.run(islem="liste")
    assert "Binary" in sonuc or "uzantı" in sonuc


def test_run_ekle():
    sonuc = binary_extensions.run(islem="ekle", uzanti=".xyz")
    assert "eklendi" in sonuc


def test_run_ekle_no_dot():
    sonuc = binary_extensions.run(islem="ekle", uzanti="abc")
    assert "eklendi" in sonuc


def test_run_ekle_no_ext():
    sonuc = binary_extensions.run(islem="ekle")
    assert "Hata" in sonuc


def test_run_invalid_islem():
    sonuc = binary_extensions.run(islem="gecersiz")
    assert "Geçersiz" in sonuc
