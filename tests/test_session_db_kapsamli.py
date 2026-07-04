"""Test: reymen/core/session_db.py — kapsamli coverage"""

from __future__ import annotations
import os, sys, json, sqlite3, time, tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


def _create_base_tables(con):
    """Test yardimcisi: session_db.py'deki INSERT ile uyumlu tablolar"""
    con.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL DEFAULT 'test',
            user_id TEXT,
            model TEXT,
            system_prompt TEXT,
            title TEXT,
            parent_session_id TEXT,
            started_at REAL NOT NULL,
            ended_at REAL,
            message_count INTEGER DEFAULT 0,
            tool_call_count INTEGER DEFAULT 0,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS session_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            rol TEXT NOT NULL,
            icerik TEXT,
            created_at REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );
    """)
    con.commit()


class TestSessionDBBaglanti:
    """_baglan ve _idempotent_tablolar — L43-78"""

    def test_baglan_connection_olusturur(self):
        """L43-51: Gecerli bir baglanti doner"""
        from reymen.core.session_db import _baglan

        td = Path(tempfile.mkdtemp())
        db_yol = td / "test.db"
        con = _baglan(db_yol)
        assert con is not None
        assert con.total_changes >= 0
        con.close()

    def test_baglan_klasor_olusturur(self):
        """L46: parent klasor yoksa olusturur"""
        from reymen.core.session_db import _baglan

        td = Path(tempfile.mkdtemp())
        db_yol = td / "alt" / "test.db"
        con = _baglan(db_yol)
        assert db_yol.exists()
        con.close()

    def test_baglan_wal_modu(self):
        """L48: WAL modu aktif"""
        from reymen.core.session_db import _baglan

        td = Path(tempfile.mkdtemp())
        con = _baglan(td / "wal_test.db")
        journal = con.execute("PRAGMA journal_mode").fetchone()[0]
        assert journal == "wal"
        con.close()

    def test_idempotent_tablolar_fts5_olusur(self):
        """L54-77: FTS5 tablolari olusur (base tablolar degil)"""
        from reymen.core.session_db import _baglan, _idempotent_tablolar

        td = Path(tempfile.mkdtemp())
        con = _baglan(td / "test.db")
        _idempotent_tablolar(con)
        tables = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' OR type='virtual'"
        ).fetchall()
        table_names = [t[0] for t in tables]
        assert "session_messages_fts" in table_names
        assert "session_messages_trigram" in table_names
        con.close()

    def test_idempotent_ikinci_cagri_hata_vermez(self):
        """L61: IF NOT EXISTS -> ikinci cagri hata firlatmaz"""
        from reymen.core.session_db import _baglan, _idempotent_tablolar

        td = Path(tempfile.mkdtemp())
        con = _baglan(td / "test.db")
        _idempotent_tablolar(con)
        _idempotent_tablolar(con)
        assert True
        con.close()

    def test_baglan_varsayilan_yol(self):
        """L45: db_yol verilmezse DB_YOLU kullanilir"""
        from reymen.core.session_db import _baglan

        with patch(
            "reymen.core.session_db.DB_YOLU", Path(tempfile.mkdtemp()) / "default.db"
        ):
            con = _baglan()
            assert con is not None
            con.close()


class TestSessionCrud:
    """session_olustur, session_getir, session_listele — L94-221"""

    def _setup_db(self, td):
        """Helper: create full DB with base tables + FTS5"""
        from reymen.core.session_db import _baglan, _idempotent_tablolar

        db_yol = td / "test.db"
        con = _baglan(db_yol)
        _create_base_tables(con)
        _idempotent_tablolar(con)
        con.close()
        return db_yol

    def test_session_olustur_happy_path(self):
        """L94-132: Yeni session olusur"""
        from reymen.core.session_db import session_olustur

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        sonuc = session_olustur(
            source="test",
            user_id="user1",
            model="gpt4",
            title="Test Session",
            db_yol=db_yol,
        )
        assert "id" in sonuc
        assert sonuc.get("source") == "test"

    def test_session_olustur_uuid_donner(self):
        """L111: UUID formatinda id"""
        from reymen.core.session_db import session_olustur

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        sonuc = session_olustur(db_yol=db_yol)
        assert len(sonuc["id"]) > 20

    def test_session_getir_var(self):
        """L135-175: Session var -> session + mesajlar"""
        from reymen.core.session_db import session_olustur, session_getir

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        olusan = session_olustur(db_yol=db_yol)
        sonuc = session_getir(olusan["id"], db_yol=db_yol)
        assert "session" in sonuc
        assert sonuc["session"]["id"] == olusan["id"]

    def test_session_getir_yok(self):
        """L154-155: Session yok -> hata"""
        from reymen.core.session_db import session_getir

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        sonuc = session_getir("olmayan-id-123", db_yol=db_yol)
        assert "hata" in sonuc
        assert "bulunamadi" in sonuc["hata"]

    def test_session_listele_bos(self):
        """L178-221: Bos DB -> []"""
        from reymen.core.session_db import session_listele

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        liste = session_listele(db_yol=db_yol)
        assert liste == []

    def test_session_listele_dolu(self):
        from reymen.core.session_db import session_olustur, session_listele

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        session_olustur(source="tg", db_yol=db_yol)
        session_olustur(source="web", db_yol=db_yol)
        liste = session_listele(db_yol=db_yol)
        assert len(liste) == 2

    def test_session_listele_filtre(self):
        """L196-205: source filtresi"""
        from reymen.core.session_db import session_olustur, session_listele

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        session_olustur(source="telegram", db_yol=db_yol)
        session_olustur(source="web", db_yol=db_yol)
        liste = session_listele(source="telegram", db_yol=db_yol)
        assert len(liste) == 1
        assert liste[0]["source"] == "telegram"


class TestMesajIslemleri:
    """mesaj_ekle — L228-291"""

    def _setup_db(self, td):
        from reymen.core.session_db import _baglan, _idempotent_tablolar

        db_yol = td / "test.db"
        con = _baglan(db_yol)
        _create_base_tables(con)
        _idempotent_tablolar(con)
        con.close()
        return db_yol

    def test_mesaj_ekle_basarili(self):
        """L228-291: Mesaj eklenir, message_count artar"""
        from reymen.core.session_db import session_olustur, mesaj_ekle, session_getir

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        s = session_olustur(db_yol=db_yol)
        r = mesaj_ekle(s["id"], "user", "Merhaba dunya", db_yol=db_yol)
        assert r.get("basarili") is True
        assert r.get("id") is not None
        detay = session_getir(s["id"], db_yol=db_yol)
        assert detay["session"]["message_count"] == 1

    def test_mesaj_ekle_session_yok(self):
        """L257-258: Session yoksa hata"""
        from reymen.core.session_db import mesaj_ekle

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        r = mesaj_ekle("olmayan-id", "user", "test", db_yol=db_yol)
        assert "hata" in r

    def test_mesaj_ekle_coklu_mesaj(self):
        """Ardisik mesaj ekleme"""
        from reymen.core.session_db import session_olustur, mesaj_ekle, session_getir

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        s = session_olustur(db_yol=db_yol)
        for i in range(3):
            mesaj_ekle(s["id"], "user", f"Mesaj {i}", db_yol=db_yol)
        detay = session_getir(s["id"], db_yol=db_yol)
        assert detay["session"]["message_count"] == 3
        assert len(detay["mesajlar"]) == 3


class TestArama:
    """mesaj_ara ve alt fonksiyonlar — L294-469"""

    def _setup_db(self, td):
        from reymen.core.session_db import _baglan, _idempotent_tablolar

        db_yol = td / "test.db"
        con = _baglan(db_yol)
        _create_base_tables(con)
        _idempotent_tablolar(con)
        con.close()
        return db_yol

    def test_mesaj_ara_fts5(self):
        """FTS5 ile arama"""
        from reymen.core.session_db import session_olustur, mesaj_ekle, mesaj_ara

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        s = session_olustur(db_yol=db_yol)
        mesaj_ekle(s["id"], "user", "bugun hava cok guzel", db_yol=db_yol)
        mesaj_ekle(s["id"], "user", "Python ile kod yaziyorum", db_yol=db_yol)
        import time as _time

        _time.sleep(0.1)  # FTS5 index'ini guncelle
        sonuc = mesaj_ara("hava", limit=5, db_yol=db_yol)
        assert len(sonuc) >= 1

    def test_mesaj_ara_bos(self):
        """Eslesme yok -> []"""
        from reymen.core.session_db import session_olustur, mesaj_ekle, mesaj_ara

        td = Path(tempfile.mkdtemp())
        db_yol = self._setup_db(td)
        s = session_olustur(db_yol=db_yol)
        mesaj_ekle(s["id"], "user", "test mesaji", db_yol=db_yol)
        sonuc = mesaj_ara("varolmayankelime", limit=5, db_yol=db_yol)
        assert sonuc == []

    def test_sync_fts5_basarili(self):
        """L80-87: FTS5 rebuild"""
        from reymen.core.session_db import _sync_fts5, _baglan, _idempotent_tablolar

        td = Path(tempfile.mkdtemp())
        db_yol = td / "test.db"
        con = _baglan(db_yol)
        _create_base_tables(con)
        _idempotent_tablolar(con)
        r = _sync_fts5(con)
        assert r == 1
        con.close()

    def test_sync_fts5_hatali(self):
        """L85-87: FTS5 rebuild hatasi -> 0"""
        from reymen.core.session_db import _sync_fts5

        td = Path(tempfile.mkdtemp())
        con = sqlite3.connect(str(td / "no_fts.db"))
        r = _sync_fts5(con)
        assert r == 0
        con.close()

    def test_like_fallback(self):
        """FTS5 yoksa LIKE fallback calisir"""
        from reymen.core.session_db import (
            _baglan,
            _idempotent_tablolar,
            session_olustur,
            mesaj_ekle,
            mesaj_ara,
        )

        td = Path(tempfile.mkdtemp())
        db_yol = td / "test.db"
        con = _baglan(db_yol)
        _create_base_tables(con)
        # FTS5 tablolarini OLUSTURMA -> LIKE fallback calismali
        con.close()
        s = session_olustur(db_yol=db_yol)
        mesaj_ekle(s["id"], "user", "like ile bulunacak metin", db_yol=db_yol)
        sonuc = mesaj_ara("like", limit=5, db_yol=db_yol)
        # LIKE fallback ile bulmali
        assert len(sonuc) >= 1


class TestMotorTools:
    """Motor tool'lari — L570-665"""

    def test_session_ara_bos_sorgu(self):
        from reymen.core.session_db import _session_ara

        r = _session_ara(sorgu="")
        assert "Kullanim" in r

    def test_session_getir_bos_id(self):
        from reymen.core.session_db import _session_getir

        r = _session_getir(session_id="")
        assert "Kullanim" in r

    def test_motor_kaydet(self):
        from reymen.core.session_db import motor_kaydet

        class M:
            tools = set()

            def _plugin_arac_kaydet(self, a, f, d=""):
                self.tools.add(a)

        m = M()
        motor_kaydet(m)
        assert "SESSION_ARA" in m.tools
        assert "SESSION_GETIR" in m.tools
        assert "SESSION_LISTE" in m.tools
