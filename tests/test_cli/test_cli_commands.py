"""Tests for reymen.sistem.cli_commands."""
import pytest
from unittest.mock import patch
from src.reymen.sistem.cli_commands import load_cli_config


class TestLoadCliConfig:
    def test_returns_dict_or_none(self):
        result = load_cli_config()
        # Config varsa dict, yoksa None/fallback
        assert result is None or isinstance(result, dict)

    def test_called_twice_same(self):
        r1 = load_cli_config()
        r2 = load_cli_config()
        assert type(r1) == type(r2)
