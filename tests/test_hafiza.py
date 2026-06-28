# -*- coding: utf-8 -*-
"""tests/test_hafiza.py — Bellek modulleri testleri."""

import sys
import os
import json
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from memory_manager import MemoryManager
from memory_provider import JsonBackend, SQLiteBackend
from context_references import ReferansYoneticisi


class TestMemoryManager:
    def test_memory_manager_olusturma(self):
        """MemoryManager baslatma."""
        mm = MemoryManager()
        assert mm is not None
        assert mm._max_kisa == 100
        assert mm._max_uzun == 1000

    def test_hatirla_kisa_bellek(self):
        """Kisa sureli bellege kaydet ve oku."""
        mm = MemoryManager()
        mm.hatirla("test_key", "test_value", sure="kisa")
        sonuc = mm.oku("test_key")
        assert sonuc == "test_value"

    def test_hatirla_uzun_bellek(self):
        """Uzun sureli bellege kaydet ve oku."""
        mm = MemoryManager()
        mm.hatirla("kalici_key", "kalici_deger", sure="uzun")
        sonuc = mm.oku("kalici_key")
        assert sonuc == "kalici_deger"

    def test_hatirla_bulunamadi(self):
        """Bulunamayan anahtar icin None donmeli."""
        mm = MemoryManager()
        sonuc = mm.oku("olmayan_anahtar")
        assert sonuc is None

    def test_ara_kisa_bellek(self):
        """Kisa bellek icinde arama."""
        mm = MemoryManager()
        mm.hatirla("kullanici_adi", "marko", sure="kisa")
        sonuclar = mm.ara("kullanici")
        assert len(sonuclar) > 0

    def test_ara_bos(self):
        """Bos bellegi arama."""
        mm = MemoryManager()
        sonuclar = mm.ara("olmayan")
        assert isinstance(sonuclar, list)

    def test_unut_kisa(self):
        """Kisa bellekten silme."""
        mm = MemoryManager()
        mm.hatirla("gecici", "deger", sure="kisa")
        mm.unut("gecici")
        assert mm.oku("gecici") is None

    def test_unut_uzun(self):
        """Uzun bellekten silme."""
        mm = MemoryManager()
        mm.hatirla("kalici", "deger", sure="uzun")
        mm.unut("kalici")
        assert mm.oku("kalici") is None

    def test_ozel_max_degerler(self):
        """Ozel max degerler ile baslatma."""
        mm = MemoryManager(max_kisa_bellek=10, max_uzun_bellek=50)
        assert mm._max_kisa == 10
        assert mm._max_uzun == 50

    def test_kisa_bellek_temizle(self):
        """Kisa bellek temizleme."""
        mm = MemoryManager()
        mm.hatirla("a", "1", sure="kisa")
        mm.hatirla("b", "2", sure="kisa")
        mm.temizle("kisa")
        assert len(mm._kisa_bellek) == 0

    def test_erisim_sayisi(self):
        """Erisim sayisi takibi."""
        mm = MemoryManager()
        mm.hatirla("populer", "deger", sure="kisa")
        mm.oku("populer")
        mm.oku("populer")
        assert mm._erisim_sayisi.get("populer", 0) >= 2


class TestMemoryProvider:
    def test_json_backend_olusturma(self):
        """JsonBackend baslatma."""
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "test_memory.json")
            jb = JsonBackend(dosya_yolu=dosya)
            assert jb is not None

    def test_json_backend_kaydet_ve_sorgula(self):
        """JsonBackend kaydetme ve sorgulama."""
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "test_memory.json")
            jb = JsonBackend(dosya_yolu=dosya)
            jb.kaydet("test_koleksiyon", {"id": 1, "deger": "test"})
            sonuclar = jb.sorgula("test_koleksiyon", "")
            assert len(sonuclar) >= 1

    def test_json_backend_bos_koleksiyon(self):
        """Bos koleksiyon sorgulama."""
        with tempfile.TemporaryDirectory() as tmp:
            dosya = os.path.join(tmp, "test_memory.json")
            jb = JsonBackend(dosya_yolu=dosya)
            sonuclar = jb.sorgula("olmayan", "")
            assert isinstance(sonuclar, list)

    def test_sqlite_backend(self):
        """SQLiteBackend (varsa)."""
        with tempfile.TemporaryDirectory() as tmp:
            db_yolu = os.path.join(tmp, "test.db")
            if SQLiteBackend:
                sb = SQLiteBackend(db_yolu=db_yolu)
                assert sb is not None
                sb.kapat()  # Windows'ta temp dir silinmeden once baglantiyi kapat


class TestContextReferences:
    def test_referans_yoneticisi_olusturma(self):
        """ReferansYoneticisi baslatma."""
        cr = ReferansYoneticisi()
        assert cr is not None
