# -*- coding: utf-8 -*-
"""Test: dizin_listele.py — Dizin listeleme aracı."""

import json
import os
from tools import dizin_listele


def test_run_current_dir():
    sonuc = dizin_listele.run(".")
    data = json.loads(sonuc)
    assert "dizin" in data
    assert "klasorler" in data
    assert "dosyalar" in data


def test_run_nonexistent():
    sonuc = dizin_listele.run("/nonexistent_path_xyz")
    data = json.loads(sonuc)
    assert "hata" in data


def test_run_file_instead():
    tmpfile = "__test_dummy__.txt"
    try:
        with open(tmpfile, "w") as f:
            f.write("test")
        sonuc = dizin_listele.run(tmpfile)
        data = json.loads(sonuc)
        assert "hata" in data
        assert "Dizin değil" in data["hata"]
    finally:
        if os.path.exists(tmpfile):
            os.unlink(tmpfile)


def test_run_default():
    sonuc = dizin_listele.run()
    data = json.loads(sonuc)
    assert "dizin" in data
