# -*- coding: utf-8 -*-
"""Test: file_state.py — Dosya durum izleyici."""

import json
import os
from tools import file_state


def test_run_kontrol(tmp_path):
    dosya = tmp_path / "test.txt"
    dosya.write_text("merhaba")
    sonuc = file_state.run("kontrol", str(dosya))
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"
    assert "bilgi" in data


def test_run_kontrol_nonexistent():
    sonuc = file_state.run("kontrol", "/nonexistent_xyz.txt")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_kontrol_no_path():
    sonuc = file_state.run("kontrol", "")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_izle(tmp_path):
    dosya = tmp_path / "test_izle.txt"
    dosya.write_text("izlenecek")
    sonuc = file_state.run("izle", str(dosya))
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"
    assert "ilk_hash" in data


def test_run_izle_nonexistent():
    sonuc = file_state.run("izle", "/nonexistent.txt")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_karsilastir(tmp_path):
    d1 = tmp_path / "a.txt"
    d2 = tmp_path / "b.txt"
    d1.write_text("aynı")
    d2.write_text("aynı")
    sonuc = file_state.run("karsilastir", f"{d1},{d2}")
    data = json.loads(sonuc)
    assert data.get("durum") == "basarili"


def test_run_karsilastir_no_comma():
    sonuc = file_state.run("karsilastir", "tek_dosya")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"


def test_run_invalid_islem():
    sonuc = file_state.run("bilinmeyen", "")
    data = json.loads(sonuc)
    assert data.get("durum") == "hata"
