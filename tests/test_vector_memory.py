# -*- coding: utf-8 -*-
"""test_vector_memory.py — VectorMemory birim testleri."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.vector_memory import VectorMemory


@pytest.fixture
def vm():
    """Gecici dizinde VectorMemory ornegi."""
    v = VectorMemory(
        koleksiyon_adi="test_koleksiyon",
        kalici_dizin=str(Path(tempfile.mkdtemp())),
    )
    yield v


# ── Happy Path ──────────────────────────────────────────────────────────


class TestVektorEkle:
    def test_ekle_bos_metin(self):
        """Bos metin eklenemez → bos string doner."""
        v = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        kid = v.ekle("")
        assert kid == ""

    def test_ekle_bosluk_metin(self):
        """Sadece bosluk metin eklenemez."""
        v = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        kid = v.ekle("   ")
        assert kid == ""


class TestVektorAra:
    def test_ara_bos_sorgu(self):
        """Bos sorgu → bos liste."""
        v = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        sonuclar = v.ara("")
        assert sonuclar == []
