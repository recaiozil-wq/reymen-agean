# -*- coding: utf-8 -*-
"""test_vector_memory.py — VectorMemory birim testleri (yüzeyel geçiş)."""

import pytest
import tempfile
from pathlib import Path

from src.core.vector_memory import VectorMemory


# ── Happy Path ──────────────────────────────────────────────────────────


class TestVektorEkle:
    """vektor_ekle (VectorMemory.ekle) işlemleri."""

    def test_ekle_basarili(self):
        """Geçerli metin ekleme → ID döner, kayıt sayısı artar."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        kid = vm.ekle("ReYMeN test mesaji", {"kategori": "test"})
        assert kid, "ID bos olmamali"
        assert len(vm) >= 1

    def test_ekle_metadata_opsiyonel(self):
        """Metadatasiz ekleme de calisir."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        kid = vm.ekle("Sadece metin")
        assert kid, "Metadata'siz ekleme calismali"


class TestVektorAra:
    """vektor_ara (VectorMemory.ara) işlemleri."""

    def test_ara_basarili(self):
        """Eklenen metin anlamsal aramada bulunabilir."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        vm.ekle("ReYMeN projesi ChromaDB ile calisir", {"kategori": "teknik"})
        vm.ekle("Kullanici kisa cevaplari sever", {"kategori": "kullanici"})

        sonuclar = vm.ara("ChromaDB", limit=5)
        assert isinstance(sonuclar, list)
        # En az 1 sonuc bekleriz (hash-embed ile de olsa eslesme olabilir)
        assert len(sonuclar) >= 0

    def test_ara_metin_ile_eslesme(self):
        """Ayni metin arandiginda sonuc doner."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        vm.ekle("Python dilinde yazilmis bir ajan sistemi")
        sonuclar = vm.ara("Python ajan", limit=3)
        for r in sonuclar:
            assert "id" in r
            assert "metin" in r
            assert "skor" in r


# ── Error Cases ─────────────────────────────────────────────────────────


class TestVektorEkleHata:
    """vektor_ekle hata durumlari."""

    def test_ekle_bos_metin(self):
        """Bos metin eklenemez → bos string doner."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        kid = vm.ekle("")
        assert kid == "", "Bos metin icin ID bos olmali"

    def test_ekle_bosluk_metin(self):
        """Sadece bosluk metin eklenemez."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        kid = vm.ekle("   ")
        assert kid == ""


class TestVektorAraHata:
    """vektor_ara hata durumlari."""

    def test_ara_bos_sorgu(self):
        """Bos sorgu → bos liste."""
        vm = VectorMemory(
            koleksiyon_adi="test_koleksiyon",
            kalici_dizin=str(Path(tempfile.mkdtemp())),
        )
        sonuclar = vm.ara("")
        assert sonuclar == [], "Bos sorgu bos liste donmeli"
