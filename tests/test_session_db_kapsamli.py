# -*- coding: utf-8 -*-
"""Test: reymen/hafiza/session_db.py — AdvancedSessionStorage kapsamli coverage"""

from __future__ import annotations
import os, sys, json, sqlite3, time, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestSessionDBBaglanti:
    """AdvancedSessionStorage baglanti testleri"""

    def test_olustur_wal_modu(self):
        """WAL modu aktif"""
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        db_yol = str(td / "test.db")
        storage = AdvancedSessionStorage(db_yolu=db_yol)
        con = storage._baglan()
        journal = con.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal == "wal"
        con.close()

    def test_klasor_olusturur(self):
        """Parent klasor yoksa olusturur"""
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        db_yol = str(td / "alt" / "test.db")
        storage = AdvancedSessionStorage(db_yolu=db_yol)
        assert Path(db_yol).exists()


class TestSessionCrud:
    """session_baslat, session_bul, son_sessionlar testleri"""

    def test_session_baslat_basarili(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test", user_id="user1", model="gpt4", title="Test Session")
        assert sid is not None
        assert len(sid) > 20

    def test_session_bul_var(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test")
        row = storage.session_bul(sid)
        assert row["id"] == sid

    def test_session_bul_yok(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        row = storage.session_bul("olmayan-id-123")
        assert row == {}

    def test_son_sessionlar_bos(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        liste = storage.son_sessionlar()
        assert liste == []

    def test_son_sessionlar_dolu(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        storage.session_baslat(source="tg")
        storage.session_baslat(source="web")
        liste = storage.son_sessionlar()
        assert len(liste) == 2

    def test_son_sessionlar_filtre(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        storage.session_baslat(source="telegram")
        storage.session_baslat(source="web")
        liste = storage.son_sessionlar(source="telegram")
        assert len(liste) == 1
        assert liste[0]["source"] == "telegram"


class TestMesajIslemleri:
    """mesaj_ekle testleri"""

    def test_mesaj_ekle_basarili(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test")
        storage.mesaj_ekle(sid, "user", "Merhaba dunya")
        row = storage.session_bul(sid)
        assert row["message_count"] == 1

    def test_mesaj_ekle_coklu(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test")
        for i in range(3):
            storage.mesaj_ekle(sid, "user", f"Mesaj {i}")
        row = storage.session_bul(sid)
        assert row["message_count"] == 3


class TestArama:
    """mesaj_ara testleri"""

    def test_mesaj_ara_fts5(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test")
        storage.mesaj_ekle(sid, "user", "bugun hava cok guzel")
        storage.mesaj_ekle(sid, "user", "Python ile kod yaziyorum")
        time.sleep(0.1)
        sonuc = storage.mesaj_ara("hava", limit=5)
        assert len(sonuc) >= 1

    def test_mesaj_ara_bos(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test")
        storage.mesaj_ekle(sid, "user", "test mesaji")
        sonuc = storage.mesaj_ara("varolmayankelime", limit=5)
        assert sonuc == []


class TestIstatistik:
    """istatistik testleri"""

    def test_istatistik_bos(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        stats = storage.istatistik()
        assert stats["toplam_session"] == 0


class TestSessionBitir:
    """session_bitir testleri"""

    def test_session_bitir(self):
        from reymen.hafiza.session_db import AdvancedSessionStorage

        td = Path(tempfile.mkdtemp())
        storage = AdvancedSessionStorage(db_yolu=str(td / "test.db"))
        sid = storage.session_baslat(source="test")
        storage.session_bitir(sid, end_reason="completed")
        row = storage.session_bul(sid)
        assert row["end_reason"] == "completed"
        assert row["ended_at"] is not None
