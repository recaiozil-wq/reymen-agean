# -*- coding: utf-8 -*-
"""Test: sistem_bilgisi.py — Sistem bilgisi aracı."""

import json
from tools import sistem_bilgisi


def test_run_returns_json():
    sonuc = sistem_bilgisi.run()
    data = json.loads(sonuc)
    assert "os" in data
    assert "python" in data
    assert "cwd" in data


def test_run_has_os_info():
    sonuc = sistem_bilgisi.run()
    data = json.loads(sonuc)
    assert data["os"] in ("Windows", "Linux", "Darwin") or len(data["os"]) > 0


def test_run_with_args():
    sonuc = sistem_bilgisi.run("extra_arg")
    data = json.loads(sonuc)
    assert "os" in data
