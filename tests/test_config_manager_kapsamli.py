"""Test: reymen/core/config_manager.py — comprehensive."""

from __future__ import annotations
import json, os, sys, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestConfigInit:
    def test_default_init(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml")
            assert c is not None

    def test_init_with_profile(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml", profil="test")
            assert c is not None

    def test_init_with_existing_file(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            yp = Path(td) / "config.yaml"
            yp.write_text("general:\n  default_model: test-model\n", encoding="utf-8")
            c = Config(config_yolu=yp)
            assert c.get("general.default_model") == "test-model"


class TestConfigGet:
    def test_get_simple_key(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            yp = Path(td) / "config.yaml"
            yp.write_text("model: deepseek\n", encoding="utf-8")
            c = Config(config_yolu=yp)
            assert c.get("model") == "deepseek"

    def test_get_nested(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            yp = Path(td) / "config.yaml"
            yp.write_text("general:\n  default_model: deepseek\n", encoding="utf-8")
            c = Config(config_yolu=yp)
            assert c.get("general.default_model") == "deepseek"

    def test_get_default(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml")
            assert c.get("olmayan", "varsayilan") == "varsayilan"

    def test_get_missing(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml")
            assert c.get("olmayan") is None


class TestConfigSet:
    def test_set_and_get(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml")
            assert c.set("test_key", "test_value") is True
            assert c.get("test_key") == "test_value"


class TestConfigPath:
    def test_get_path(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            yp = Path(td) / "config.yaml"
            yp.write_text("logs: /var/log\n", encoding="utf-8")
            c = Config(config_yolu=yp)
            result = c.get_path("logs")
            # Windows'ta WindowsPath otomatik C: ekler
            assert str(result).endswith("/var/log") or str(result).endswith(
                "\\var\\log"
            )


class TestConfigEnv:
    def test_get_env(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml")
            with patch.dict(os.environ, {"TEST_VAR": "env_val"}, clear=True):
                assert c.get_env("TEST_VAR") == "env_val"


class TestConfigProvider:
    def test_get_provider(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            yp = Path(td) / "config.yaml"
            yp.write_text(
                "providers:\n  deepseek:\n    api_key: sk-test\n", encoding="utf-8"
            )
            c = Config(config_yolu=yp)
            p = c.get_provider("deepseek")
            assert p is not None

    def test_get_provider_yok(self):
        from reymen.core.config_manager import Config

        with tempfile.TemporaryDirectory() as td:
            c = Config(config_yolu=Path(td) / "config.yaml")
            assert c.get_provider("yok") is None


class TestSingleton:
    def test_varsayilan_config(self):
        from reymen.core.config_manager import varsayilan_config

        with tempfile.TemporaryDirectory() as td:
            with patch("reymen.core.config_manager._PROJE_KOKU", Path(td)):
                c1 = varsayilan_config()
                c2 = varsayilan_config()
                assert c1 is c2
