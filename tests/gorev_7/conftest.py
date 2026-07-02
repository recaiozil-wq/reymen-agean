"""Test ortami icin ortak fixture ve ayarlar."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Proje kokunu Python path'e ekle
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture(autouse=True)
def _isolate_reymen_home(tmp_path, monkeypatch):
    """Her test icin izole ReYMeN_HOME dizini."""
    monkeypatch.setenv("ReYMeN_HOME", str(tmp_path / ".ReYMeN"))
    yield


@pytest.fixture
def tmp_db(tmp_path):
    """Gecici SQLite veritabani yolu."""
    return tmp_path / "test.db"
