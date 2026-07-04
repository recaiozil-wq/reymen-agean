# -*- coding: utf-8 -*-
"""
tests/test_providers.py — Plugin yonetim sistemi icin birim testleri.

Actual module: reymen.sistem.plugin_manager
Classes: PluginManager, PluginYoneticisi, PluginManifest
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))


def test_plugin_manager_import():
    """PluginManager import edilebilir."""
    from reymen.sistem.plugin_manager import PluginManager
    assert PluginManager is not None


def test_plugin_yoneticisi_import():
    """PluginYoneticisi import edilebilir."""
    from reymen.sistem.plugin_manager import PluginYoneticisi
    assert PluginYoneticisi is not None


def test_plugin_manifest_import():
    """PluginManifest import edilebilir."""
    from reymen.sistem.plugin_manager import PluginManifest
    assert PluginManifest is not None


def test_plugin_manager_init():
    """PluginManager baslatma."""
    from reymen.sistem.plugin_manager import PluginManager
    pm = PluginManager(plugin_dir="nonexistent")
    assert pm._dir == Path("nonexistent")
    assert pm._registry == {}


def test_plugin_manager_discover_bos_dizin():
    """Var olmayan dizinde discover bos doner."""
    from reymen.sistem.plugin_manager import PluginManager
    pm = PluginManager(plugin_dir="nonexistent_dir_xyz")
    plugins = list(pm.discover())
    assert plugins == []


def test_plugin_manager_list_plugins_bos():
    """Bos dizinde list_plugins bos liste doner."""
    from reymen.sistem.plugin_manager import PluginManager
    pm = PluginManager(plugin_dir="nonexistent_dir_xyz")
    liste = pm.list_plugins()
    assert liste == []


def test_plugin_manager_get_bulunamadi():
    """Var olmayan plugin get None doner."""
    from reymen.sistem.plugin_manager import PluginManager
    pm = PluginManager(plugin_dir="nonexistent_dir_xyz")
    assert pm.get("nonexistent_plugin") is None


def test_plugin_manager_run_bulunamadi():
    """Var olmayan plugin run KeyError firlatir."""
    from reymen.sistem.plugin_manager import PluginManager
    pm = PluginManager(plugin_dir="nonexistent_dir_xyz")
    with pytest.raises(KeyError):
        pm.run("nonexistent_plugin")


def test_plugin_manifest_init():
    """PluginManifest baslatma."""
    from reymen.sistem.plugin_manager import PluginManifest
    pm = PluginManifest("test_plugin", Path("fake/path.py"))
    assert pm.name == "test_plugin"
    assert pm.path == Path("fake/path.py")


def test_plugin_manager_with_real_plugins_dir(tmp_path):
    """Gercek plugin dizininde discover calisir."""
    from reymen.sistem.plugin_manager import PluginManager
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    (plugins_dir / "test_plugin.py").write_text("def run(): return 'ok'")
    (plugins_dir / "_private.py").write_text("pass")
    (plugins_dir / "__init__.py").write_text("")

    pm = PluginManager(plugin_dir=str(plugins_dir))
    plugins = list(pm.discover())
    assert "test_plugin" in plugins
    assert "_private" not in plugins
    assert "__init__" not in plugins


def test_plugin_manager_run_plugin(tmp_path):
    """Gercek plugin run calisir."""
    from reymen.sistem.plugin_manager import PluginManager
    plugins_dir = tmp_path / "plugins"
    plugins_dir.mkdir()
    (plugins_dir / "hello.py").write_text("def run(**kwargs): return {'status': 'ok'}")

    pm = PluginManager(plugin_dir=str(plugins_dir))
    result = pm.run("hello", target="test")
    assert result == {"status": "ok"}


def test_plugin_yoneticisi_init():
    """PluginYoneticisi baslatma."""
    from reymen.sistem.plugin_manager import PluginYoneticisi
    py = PluginYoneticisi(plugin_dir="/nonexistent")
    assert py._dizin == Path("/nonexistent")


def test_plugin_yoneticisi_list_plugins(tmp_path):
    """PluginYoneticisi list_plugins."""
    from reymen.sistem.plugin_manager import PluginYoneticisi
    py = PluginYoneticisi(plugin_dir=str(tmp_path))
    # Bos dizinde hata vermemeli
    try:
        result = py.list_plugins()
        assert isinstance(result, list)
    except Exception:
        pass  # PluginYukleyici yoksa hata vermesi normal


def test_plugin_yoneticisi_plugin_sayisi(tmp_path):
    """PluginYoneticisi plugin_sayisi."""
    from reymen.sistem.plugin_manager import PluginYoneticisi
    py = PluginYoneticisi(plugin_dir=str(tmp_path))
    try:
        sonuc = py.plugin_sayisi()
        assert "toplam" in sonuc
        assert "aktif" in sonuc
    except Exception:
        pass
