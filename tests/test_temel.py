"""ReYMeN — Temel import ve yapi testleri."""

import importlib
import json
import os
import sys
from pathlib import Path

import pytest


def test_proje_koku_var():
    """Proje kok dizini mevcut mu?"""
    kok = Path(__file__).parent.parent
    assert (kok / "reymen").is_dir(), "reymen/ dizini yok"
    assert (kok / "reymen_launcher.py").exists(), "reymen_launcher.py yok"
    assert (kok / "durum.json").exists(), "durum.json yok"


def test_temel_moduller_import():
    """Kritik moduller sorunsuz import edilebiliyor mu?"""
    moduller = [
        "reymen.cereyan.conversation_loop",
        "reymen.cereyan.motor",
        "reymen.cereyan.beyin",
        "reymen.arac.web_search_engine",
        "reymen.arac.image_gen_engine",
    ]
    for mod in moduller:
        try:
            importlib.import_module(mod)
        except Exception as e:
            pytest.fail(f"{mod} import hatasi: {e}")


def test_mcp_client_import():
    """MCP client modulu import edilebiliyor mu?"""
    try:
        from reymen.arac.mcp_client_tool import MCPClientHTTP
        assert MCPClientHTTP is not None
    except Exception as e:
        pytest.fail(f"MCPClientHTTP import hatasi: {e}")


def test_vision_tools_import():
    """Vision tools modulu import edilebiliyor mu?"""
    try:
        from reymen.cereyan.tools.vision_tools import vision_analiz
        assert callable(vision_analiz)
    except Exception as e:
        pytest.fail(f"vision_tools import hatasi: {e}")


def test_durum_json_okunabilir():
    """durum.json gecerli JSON mu?"""
    durum_path = Path(__file__).parent.parent / "durum.json"
    assert durum_path.exists(), "durum.json yok"
    with open(durum_path, "r", encoding="utf-8") as f:
        veri = json.load(f)
    assert "proje" in veri, "proje anahtari yok"
    assert "surum" in veri, "surum anahtari yok"
    assert "botlar" in veri, "botlar anahtari yok"


def test_skills_dizini_var():
    """Skills dizininde dosyalar var mi?"""
    skills_path = Path(__file__).parent.parent / "reymen" / "cereyan" / "skills"
    assert skills_path.is_dir(), "skills/ dizini yok"
    py_files = list(skills_path.rglob("*.py"))
    md_files = list(skills_path.rglob("*.md"))
    assert len(py_files) > 0, "skills/ altinda .py dosyasi yok"
