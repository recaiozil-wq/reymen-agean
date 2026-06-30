# -*- coding: utf-8 -*-
"""
tests/test_hafiza.py — Hafıza katmanı kapsamlı testleri.

SQLite tabanlı modüller (:memory:) ile test edilir.
JSON tabanlı modüller (AltAjanHafiza) tmp_path ile test edilir.
Embedding/vektör modülleri mock ile izole edilir.
"""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, PropertyMock

import pytest

# ── Proje kökü ├───────────────────────────────────────────────────────────
PROJE_KOK = Path(__file__).resolve().parent.parent
import sys
if str(PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(PROJE_KOK))


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 1 — AdvancedSessionStorage (session_db.py)
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def in_memory_db():
    """Her test için sıfır, temiz bir in-memory SQLite veritabanı.

    AdvancedSessionStorage şemasını birebir kurar:
      - sessions
      - session_messages
      - session_tool_calls
      - ajan_gunlugu (FTS5)
      - session_messages_fts (FTS5 content-sync)
    
    WAL + foreign_keys + row_factory aktif.
    """
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id                TEXT PRIMARY KEY,
            source            TEXT NOT NULL,
            user_id           TEXT,
            model             TEXT,
            model_config      TEXT,
            system_prompt     TEXT,
            parent_session_id TEXT,
            started_at        REAL NOT NULL,
            ended_at          REAL,
            end_reason        TEXT,
            message_count     INTEGER DEFAULT 0,
            tool_call_count   INTEGER DEFAULT 0,
            input_tokens      INTEGER DEFAULT 0,
            output_tokens     INTEGER DEFAULT 0,
            cache_read_tokens  INTEGER DEFAULT 0,
            cache_write_tokens INTEGER DEFAULT 0,
            reasoning_tokens  INTEGER DEFAULT 0,
            billing_provider  TEXT,
            billing_base_url  TEXT,
            billing_mode      TEXT,
            estimated_cost_usd REAL,
            actual_cost_usd   REAL,
            cost_status       TEXT,
            cost_source       TEXT,
            pricing_version   TEXT,
            title             TEXT,
            api_call_count    INTEGER DEFAULT 0,
            FOREIGN KEY (parent_session_id) REFERENCES sessions(id)
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_source ON sessions(source)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_parent ON sessions(parent_session_id)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at DESC)"
    )
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_sessions_title_unique "
        "ON sessions(title) WHERE title IS NOT NULL"
    )

    conn.execute("""
        CREATE TABLE IF NOT EXISTS session_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            rol        TEXT NOT NULL,
            icerik     TEXT,
            created_at REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS session_tool_calls (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  TEXT NOT NULL,
            tool_name   TEXT NOT NULL,
            args        TEXT,
            result      TEXT,
            duration_ms INTEGER,
            created_at  REAL NOT NULL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    """)

    # FTS5 ajan_gunlugu
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS ajan_gunlugu USING fts5(
            hedef, eylem, sonuc
        )
    """)

    # FTS5 session_messages (content-sync)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS session_messages_fts USING fts5(
            session_id UNINDEXED,
            rol UNINDEXED,
            icerik,
            content='session_messages',
            content_rowid='id'
        )
    """)

    conn.commit()
    yield conn
    conn.close()


class _NoCloseConnection:
    """SQLite bağlantı sarmalayıcısı: close()'u pas geçer.

    AdvancedSessionStorage her metodda _baglan() + conn.close() yapar.
    :memory: DB'de close() tüm veriyi siler. Bu sarmalayıcı close'u
    no-op yaparak bağlantının canlı kalmasını sağlar.
    """

    def __init__(self, conn):
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    def close(self):
        pass  # NO-OP: in-memory bağlantıyı kapatma


@pytest.fixture
def ass_storage(in_memory_db):
    """AdvancedSessionStorage örneği — _baglan() mock'lu, in-memory DB ile."""
    from reymen.hafiza.session_db import AdvancedSessionStorage

    no_close = _NoCloseConnection(in_memory_db)

    def mock_baglan(self):
        """_baglan override: in-memory DB döndür, close() pas geçer."""
        return no_close

    with patch.object(AdvancedSessionStorage, '_baglan', mock_baglan):
        # _kur'u bypass et (tablolar zaten fixture'da kurulu)
        with patch.object(AdvancedSessionStorage, '_kur', lambda self: None):
            storage = AdvancedSessionStorage(":memory:")
            yield storage


# ── Testler ────────────────────────────────────────────────────────────────

class TestSessionDB:
    """AdvancedSessionStorage: session yönetimi, mesaj kaydı, arama, temizlik."""

    def test_session_baslat(self, ass_storage):
        """Session oluşturma → id döner, started_at dolu."""
        sid = ass_storage.session_baslat(
            source="test", model="deepseek", user_id="user_1"
        )
        assert sid is not None
        assert len(sid) > 0  # UUID

        session = ass_storage.session_bul(sid)
        assert session["id"] == sid
        assert session["source"] == "test"
        assert session["model"] == "deepseek"
        assert session["user_id"] == "user_1"
        assert session["started_at"] > 0
        assert session["ended_at"] is None

    def test_session_bitir(self, ass_storage):
        """Session bitirme → ended_at + end_reason set edilir."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.session_bitir(sid, end_reason="completed")
        session = ass_storage.session_bul(sid)
        assert session["ended_at"] is not None
        assert session["end_reason"] == "completed"

    def test_mesaj_ekle_ve_sayac(self, ass_storage):
        """Mesaj ekleme → message_count artar, içerik doğru kaydedilir."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.mesaj_ekle(sid, "user", "Kayseri'de hava nasıl?")
        ass_storage.mesaj_ekle(sid, "assistant", "Hava 25 derece.")

        session = ass_storage.session_bul(sid)
        assert session["message_count"] == 2

        # Doğrudan in-memory DB'den doğrula
        cursor = ass_storage._baglan().cursor()
        rows = cursor.execute(
            "SELECT rol, icerik FROM session_messages WHERE session_id=? ORDER BY id",
            (sid,),
        ).fetchall()
        assert len(rows) == 2
        assert rows[0]["rol"] == "user"
        assert rows[0]["icerik"] == "Kayseri'de hava nasıl?"
        assert rows[1]["rol"] == "assistant"

    def test_mesaj_ekle_fts_indexlenir(self, ass_storage):
        """Mesaj ekleme → FTS5 index'lenir, mesaj_ara ile bulunabilir."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.mesaj_ekle(sid, "user", "Python decorator nasıl kullanılır?")
        ass_storage.mesaj_ekle(sid, "user", "Flask ile API yazmak istiyorum.")

        # FTS5 arama
        sonuclar = ass_storage.mesaj_ara("decorator")
        assert len(sonuclar) >= 1
        assert "decorator" in sonuclar[0]["icerik"]

    def test_mesaj_ara_trigram_substring(self, ass_storage):
        """Mesaj ara trigram modu → kısmi kelime eşleşmesi."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.mesaj_ekle(sid, "user", "merhaba dünya test")
        ass_storage.mesaj_ekle(sid, "user", "python programlama dili")

        # trigram ile kısmi arama
        sonuclar = ass_storage.mesaj_ara("dünya", kismi=True)
        assert len(sonuclar) >= 1
        assert "dünya" in sonuclar[0]["icerik"]

    def test_mesaj_ara_zaman_araligi(self, ass_storage):
        """Mesaj ara zaman filtresi ile."""
        sid = ass_storage.session_baslat(source="test")
        eski_zaman = time.time() - 3600  # 1 saat önce
        yeni_zaman = time.time()

        # Zamanı manuel ayarlamak için DB'ye direkt yaz
        conn = ass_storage._baglan()
        conn.execute(
            "INSERT INTO session_messages (session_id, rol, icerik, created_at) VALUES (?,?,?,?)",
            (sid, "user", "eski mesaj", eski_zaman),
        )
        # FTS sync
        rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO session_messages_fts(rowid, session_id, rol, icerik) VALUES (?,?,?,?)",
            (rowid, sid, "user", "eski mesaj"),
        )
        conn.execute(
            "INSERT INTO session_messages (session_id, rol, icerik, created_at) VALUES (?,?,?,?)",
            (sid, "user", "yeni mesaj", yeni_zaman),
        )
        rowid2 = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO session_messages_fts(rowid, session_id, rol, icerik) VALUES (?,?,?,?)",
            (rowid2, sid, "user", "yeni mesaj"),
        )
        conn.commit()

        # Sadece yeni zaman aralığında ara
        sonuclar = ass_storage.mesaj_ara(
            "mesaj",
            baslangic_ts=yeni_zaman - 10,
            bitis_ts=yeni_zaman + 10,
        )
        assert len(sonuclar) == 1
        assert sonuclar[0]["icerik"] == "yeni mesaj"

    def test_tool_call_kaydet(self, ass_storage):
        """Tool call kaydı → tool_call_count artar."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.tool_call_kaydet(sid, "web_search", {"q": "test"}, "sonuç", 150)
        ass_storage.tool_call_kaydet(sid, "read_file", {"path": "x.txt"}, "içerik", 5)

        session = ass_storage.session_bul(sid)
        assert session["tool_call_count"] == 2
        assert session["api_call_count"] == 2

    def test_token_guncelle(self, ass_storage):
        """Token güncelleme → kümülatif artar."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.token_guncelle(sid, input_tokens=100, output_tokens=50)
        ass_storage.token_guncelle(sid, input_tokens=30, output_tokens=20)

        session = ass_storage.session_bul(sid)
        assert session["input_tokens"] == 130
        assert session["output_tokens"] == 70

    def test_maliyet_guncelle(self, ass_storage):
        """Maliyet güncelleme → estimated/actual cost kaydedilir."""
        sid = ass_storage.session_baslat(source="test")
        ass_storage.maliyet_guncelle(sid, estimated_cost=0.015, actual_cost=0.012)

        session = ass_storage.session_bul(sid)
        assert session["estimated_cost_usd"] == 0.015
        assert session["actual_cost_usd"] == 0.012

    def test_son_sessionlar(self, ass_storage):
        """Son session'lar kronolojik sırada döner."""
        sid1 = ass_storage.session_baslat(source="cli", model="a")
        time.sleep(0.01)
        sid2 = ass_storage.session_baslat(source="web", model="b")
        time.sleep(0.01)
        sid3 = ass_storage.session_baslat(source="cli", model="c")

        son = ass_storage.son_sessionlar(limit=2)
        assert len(son) == 2
        # En yeni 2 session: sid3, sid2
        assert son[0]["id"] == sid3
        assert son[1]["id"] == sid2

        # source filtresi
        cli_sessions = ass_storage.son_sessionlar(source="cli")
        assert all(s["source"] == "cli" for s in cli_sessions)
        assert len(cli_sessions) == 2

    def test_session_search_fts(self, ass_storage):
        """session_search → FTS ile session bulma."""
        sid = ass_storage.session_baslat(source="test", title="Python Eğitimi")
        ass_storage.mesaj_ekle(sid, "user", "Python decorator nedir?")
        ass_storage.mesaj_ekle(sid, "assistant", "Decorator bir fonksiyon sarmalayıcıdır.")

        sonuclar = ass_storage.session_search("decorator")
        assert len(sonuclar) >= 1
        assert sonuclar[0]["session_id"] == sid
        # session_search ozet alanı: title varsa onu kullanır
        assert "Python" in sonuclar[0]["ozet"]

    def test_istatistik(self, ass_storage):
        """İstatistik: toplam session, token, maliyet."""
        s1 = ass_storage.session_baslat(source="cli")
        ass_storage.token_guncelle(s1, input_tokens=100, output_tokens=50)
        ass_storage.maliyet_guncelle(s1, estimated_cost=0.01)

        s2 = ass_storage.session_baslat(source="web")
        ass_storage.token_guncelle(s2, input_tokens=200, output_tokens=100)

        ist = ass_storage.istatistik()
        assert ist["toplam_session"] == 2
        assert ist["toplam_input_token"] == 300
        assert ist["toplam_output_token"] == 150
        assert ist["toplam_tahmini_maliyet"] == 0.01

    def test_session_export_json(self, ass_storage):
        """Session export JSON formatı."""
        sid = ass_storage.session_baslat(source="test", model="deepseek")
        ass_storage.mesaj_ekle(sid, "user", "merhaba")
        ass_storage.mesaj_ekle(sid, "assistant", "merhaba, nasıl yardımcı olabilirim?")
        ass_storage.session_bitir(sid, end_reason="completed")

        exported = ass_storage.session_export(sid, format="json")
        assert exported
        data = json.loads(exported)
        assert data["session"]["id"] == sid
        assert len(data["messages"]) == 2

    def test_session_export_markdown(self, ass_storage):
        """Session export Markdown formatı."""
        sid = ass_storage.session_baslat(source="test", title="Test Session")
        ass_storage.mesaj_ekle(sid, "user", "merhaba")

        md = ass_storage.session_export(sid, format="markdown")
        assert md
        assert "# Test Session" in md
        assert "USER" in md
        assert "merhaba" in md

    def test_session_import(self, ass_storage):
        """Session import: JSON'dan yeni session oluşturur."""
        # Önce export
        kaynak_sid = ass_storage.session_baslat(source="original", title="Kaynak")
        ass_storage.mesaj_ekle(kaynak_sid, "user", "test mesaj")
        ass_storage.token_guncelle(kaynak_sid, input_tokens=50, output_tokens=25)
        ass_storage.session_bitir(kaynak_sid, end_reason="completed")
        export_data = ass_storage.session_export(kaynak_sid, format="json")

        # Import
        yeni_id = ass_storage.session_import(export_data)
        assert yeni_id
        assert yeni_id != kaynak_sid

        # Doğrula
        yeni_session = ass_storage.session_bul(yeni_id)
        assert yeni_session["source"] == "original"
        assert yeni_session["input_tokens"] == 50
        assert yeni_session["output_tokens"] == 25

    def test_session_temizle(self, ass_storage):
        """Eski session'ları temizleme."""
        # Eski session
        eski_id = ass_storage.session_baslat(source="test")
        # started_at'i eski yap
        conn = ass_storage._baglan()
        conn.execute(
            "UPDATE sessions SET started_at=? WHERE id=?",
            (time.time() - 100 * 86400, eski_id),  # 100 gün önce
        )
        ass_storage.session_bitir(eski_id, end_reason="completed")
        conn.commit()

        # Yeni session
        yeni_id = ass_storage.session_baslat(source="test")
        ass_storage.session_bitir(yeni_id, end_reason="completed")

        # 90 günden eski olanları temizle
        silinen = ass_storage.session_temizle(days=90)
        assert silinen >= 1

        # Eski session silinmiş olmalı, yeni durmalı
        assert ass_storage.session_bul(eski_id) == {}
        assert ass_storage.session_bul(yeni_id) != {}

    def test_gunluge_yaz(self, ass_storage):
        """FTS5 ajan_gunlugu'na yazma."""
        ass_storage.gunluge_yaz("test_hedef", "test_eylem", "test_sonuc")

        # FTS5'te ara
        conn = ass_storage._baglan()
        rows = conn.execute(
            "SELECT hedef FROM ajan_gunlugu WHERE ajan_gunlugu MATCH 'test_hedef'"
        ).fetchall()
        assert len(rows) >= 1

    def test_session_bul_bulunamadi(self, ass_storage):
        """Var olmayan session → {} döner."""
        assert ass_storage.session_bul("olmayan_id") == {}

    def test_session_baslat_model_config(self, ass_storage):
        """Model config JSON olarak kaydedilir."""
        mc = {"temperature": 0.7, "max_tokens": 2048}
        sid = ass_storage.session_baslat(
            source="test", model="deepseek", model_config=mc
        )
        session = ass_storage.session_bul(sid)
        assert json.loads(session["model_config"]) == mc


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 2 — GelismisHafiza (hafiza_genislet.py) — SQLite+FTS5
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def gelismis_hafiza():
    """GelismisHafiza örneği — :memory: DB ile, _baglan + _tablolari_olustur mock'lu."""
    # GelismisHafiza'nın _baglan + _tablolari_olustur + _hazir ayarlarını mock'la
    from reymen.hafiza.hafiza_genislet import GelismisHafiza

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    # Şema kur
    conn.execute("""
        CREATE TABLE IF NOT EXISTS kayitlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            koleksiyon TEXT NOT NULL,
            anahtar TEXT DEFAULT '',
            icerik TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            zaman REAL NOT NULL,
            expire_zaman REAL DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            baslik TEXT DEFAULT '',
            baslangic REAL NOT NULL,
            bitis REAL DEFAULT 0,
            mesaj_sayisi INTEGER DEFAULT 0,
            ozet TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tercihler (
            anahtar TEXT PRIMARY KEY,
            deger TEXT NOT NULL,
            guncelleme_zamani REAL NOT NULL
        )
    """)
    conn.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS kayitlar_fts USING fts5(
            icerik, metadata, anahtar,
            content='kayitlar',
            content_rowid='id',
            tokenize='unicode61'
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kayit_session ON kayitlar(session_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kayit_koleksiyon ON kayitlar(koleksiyon)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kayit_zaman ON kayitlar(zaman)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_kayit_expire ON kayitlar(expire_zaman)")

    # FTS5 content-sync trigger'ları
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS kayitlar_ai AFTER INSERT ON kayitlar BEGIN
            INSERT INTO kayitlar_fts(rowid, icerik, metadata, anahtar)
            VALUES (new.id, new.icerik, new.metadata, new.anahtar);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS kayitlar_ad AFTER DELETE ON kayitlar BEGIN
            INSERT INTO kayitlar_fts(kayitlar_fts, rowid, icerik, metadata, anahtar)
            VALUES ('delete', old.id, old.icerik, old.metadata, old.anahtar);
        END
    """)
    conn.execute("""
        CREATE TRIGGER IF NOT EXISTS kayitlar_au AFTER UPDATE ON kayitlar BEGIN
            INSERT INTO kayitlar_fts(kayitlar_fts, rowid, icerik, metadata, anahtar)
            VALUES ('delete', old.id, old.icerik, old.metadata, old.anahtar);
            INSERT INTO kayitlar_fts(rowid, icerik, metadata, anahtar)
            VALUES (new.id, new.icerik, new.metadata, new.anahtar);
        END
    """)
    conn.commit()

    gh = GelismisHafiza.__new__(GelismisHafiza)
    gh._db_yolu = ":memory:"
    gh._conn = conn
    gh._hazir = True
    gh._aktif_session = ""
    gh._mesaj_sayaci = 0
    gh._otomatik_kayit_esigi = 10

    yield gh
    conn.close()


class TestGelismisHafiza:
    """GelismisHafiza: kayıt, FTS5 arama, session yönetimi, context compression."""

    def test_initialize_session(self, gelismis_hafiza):
        """Session başlatma → sessions tablosuna kayıt."""
        gh = gelismis_hafiza
        gh.initialize("session_test_1", baslik="Test Session")

        # Doğrudan sqlite ile doğrula
        c = gh._conn.cursor()
        row = c.execute("SELECT id, baslik FROM sessions WHERE id=?", ("session_test_1",)).fetchone()
        assert row["id"] == "session_test_1"
        assert row["baslik"] == "Test Session"

    def test_session_bitir(self, gelismis_hafiza):
        """Session bitirme → bitis + mesaj_sayisi + ozet kaydedilir."""
        gh = gelismis_hafiza
        gh.initialize("s1")
        gh.kaydet("mesaj 1", "konusmalar")
        gh.kaydet("mesaj 2", "konusmalar")
        gh.session_bitir(ozet="2 mesajlı test")

        c = gh._conn.cursor()
        row = c.execute("SELECT bitis, mesaj_sayisi, ozet FROM sessions WHERE id='s1'").fetchone()
        assert row["bitis"] > 0
        assert row["mesaj_sayisi"] == 2
        assert "2 mesaj" in row["ozet"]

    def test_kaydet_ve_fts_ara(self, gelismis_hafiza):
        """Kayıt + FTS5 arama."""
        gh = gelismis_hafiza
        gh.initialize("s1")

        gh.kaydet("Python decorator nedir?", "konusmalar", anahtar="decorator")
        gh.kaydet("Flask ile API nasıl yazılır?", "konusmalar", anahtar="flask")

        sonuclar = gh.ara("decorator")
        assert len(sonuclar) >= 1
        assert "decorator" in sonuclar[0]["icerik"].lower()

    def test_kaydet_metadata_ile(self, gelismis_hafiza):
        """Metadata ile kayıt."""
        gh = gelismis_hafiza
        gh.initialize("s1")
        gh.kaydet(
            "test içerik", "notlar",
            anahtar="test",
            metadata={"onem": "yüksek", "kaynak": "web"},
        )

        sonuclar = gh.ara("test")
        assert len(sonuclar) >= 1

    def test_kaydet_ttl_expire(self, gelismis_hafiza):
        """TTL süresi geçen kayıtlar aramada görünmez."""
        gh = gelismis_hafiza
        gh.initialize("s1")
        gh.kaydet("gecici kayıt", "konusmalar", ttl_saat=0.0001)  # ~0.36 saniye
        time.sleep(0.5)

        sonuclar = gh.ara("gecici")
        assert len(sonuclar) == 0  # TTL geçti, expire oldu

    def test_kayit_guncelle(self, gelismis_hafiza):
        """Kayıt güncelleme → FTS5 trigger ile senkron."""
        gh = gelismis_hafiza
        gh.initialize("s1")
        gh.kaydet("eski içerik", "konusmalar")

        # İlk kaydın ID'sini bul
        c = gh._conn.cursor()
        row = c.execute("SELECT id FROM kayitlar LIMIT 1").fetchone()
        kayit_id = row["id"]

        gh.kayit_guncelle(kayit_id, yeni_icerik="yeni içerik")

        # FTS'de ara
        sonuclar = gh.ara("yeni")
        assert len(sonuclar) >= 1
        assert "yeni" in sonuclar[0]["icerik"]

    def test_ara_koleksiyon_filtresi(self, gelismis_hafiza):
        """Filtre: sadece belirli koleksiyonda ara."""
        gh = gelismis_hafiza
        gh.initialize("s1")
        gh.kaydet("ortak kelime", "konusmalar")
        gh.kaydet("ortak kelime", "notlar")

        konusma_sonuc = gh.ara("ortak", koleksiyon="konusmalar")
        assert all(s["koleksiyon"] == "konusmalar" for s in konusma_sonuc)

        not_sonuc = gh.ara("ortak", koleksiyon="notlar")
        assert all(s["koleksiyon"] == "notlar" for s in not_sonuc)

    def test_ara_session_filtresi(self, gelismis_hafiza):
        """Filtre: sadece belirli session'da ara."""
        gh = gelismis_hafiza
        gh.initialize("session_a")
        gh.kaydet("özel veri", "konusmalar")
        gh.session_bitir()

        gh.initialize("session_b")
        gh.kaydet("başka veri", "konusmalar")
        gh.session_bitir()

        sonuc_a = gh.ara("veri", session_id="session_a")
        assert all(s["session_id"] == "session_a" for s in sonuc_a)

    def test_arama_sirala_tam_eslesme_once(self, gelismis_hafiza):
        """arama_sirala: tam eşleşme kısmi eşleşmeden önce gelir."""
        gh = gelismis_hafiza
        gh.initialize("s1")
        gh.kaydet("Python programlama dili çok popüler", "konusmalar")
        gh.kaydet("Java programlama dili de popüler", "konusmalar")

        sonuclar = gh.arama_sirala("Python")
        assert len(sonuclar) >= 1
        # "Python" içeren ilk sırada olmalı
        assert "python" in sonuclar[0]["icerik"].lower()

    def test_tercih_al_set(self, gelismis_hafiza):
        """Kullanıcı tercihleri: set ve get."""
        gh = gelismis_hafiza

        # tercih_al metodu için doğrudan SQL sorgusu
        # (hafiza_genislet.py'nin tercih_al/tercih_ayarla metodu yoksa
        #  manuel check yap)
        c = gh._conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO tercihler (anahtar, deger, guncelleme_zamani) VALUES (?,?,?)",
            ("dil", "Türkçe", time.time()),
        )
        gh._conn.commit()

        row = c.execute("SELECT deger FROM tercihler WHERE anahtar='dil'").fetchone()
        assert row["deger"] == "Türkçe"


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 3 — AltAjanHafiza (hafiza.py) — JSON dosya tabanlı
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def alt_ajan_hafiza(tmp_path):
    """AltAjanHafiza örneği — temp dizin ile."""
    from reymen.hafiza.hafiza import AltAjanHafiza, HAFIZA_DIZINI

    # HAFIZA_DIZINI'ni tmp_path'e yönlendir
    with patch.object(
        type("HAFIZA_DIZINI_MOCK", (), {}),
        "resolve",
        return_value=tmp_path / ".alt_ajan_hafiza",
    ):
        original_path = Path("reymen/hafiza/.alt_ajan_hafiza")
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()
            yield hafiza


class TestAltAjanHafiza:
    """AltAjanHafiza: JSON dosya tabanlı hafıza, task kaydı."""

    def test_kaydet_ve_yukle(self, tmp_path):
        """Kayıt ve yükleme."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()

            hafiza.kaydet("task_001", "adim", {"adim_no": 1, "cevap": "test"})
            hafiza.kaydet("task_001", "sonuc", {"basarili": True})

            kayit = hafiza.yukle("task_001")
            assert kayit is not None
            assert len(kayit["kayitlar"]) == 2
            assert kayit["kayitlar"][0]["tur"] == "adim"
            assert kayit["kayitlar"][0]["veri"]["adim_no"] == 1

    def test_son_kayit(self, tmp_path):
        """Son kaydı döndürür."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()
            hafiza.kaydet("t1", "adim", {"no": 1})
            hafiza.kaydet("t1", "adim", {"no": 2})
            hafiza.kaydet("t1", "sonuc", {"done": True})

            son = hafiza.son_kayit("t1")
            assert son["tur"] == "sonuc"
            assert son["veri"]["done"] is True

    def test_task_listele(self, tmp_path):
        """Task'ları listeleme."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()

            hafiza.kaydet("task_a", "adim", {"a": 1})
            time.sleep(0.01)
            hafiza.kaydet("task_b", "sonuc", {"b": 2})

            liste = hafiza.task_listele()
            assert len(liste) >= 2
            # En son güncellenen ilk sırada
            assert len(liste) >= 2

    def test_temizle(self, tmp_path):
        """Task silme."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()
            hafiza.kaydet("silinecek", "adim", {"x": 1})
            assert hafiza.yukle("silinecek") is not None

            hafiza.temizle("silinecek")
            assert hafiza.yukle("silinecek") is None

    def test_temizle_hepsi(self, tmp_path):
        """Tümünü temizleme."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()
            hafiza.kaydet("t1", "adim", {})
            hafiza.kaydet("t2", "adim", {})

            silinen = hafiza.temizle_hepsi()
            assert silinen == 2
            assert hafiza.task_listele() == []

    def test_olmayan_task_none(self, tmp_path):
        """Olmayan task → None döner."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()
            assert hafiza.yukle("yok") is None
            assert hafiza.son_kayit("yok") is None

    def test_bos_listele(self, tmp_path):
        """Boş hafıza → boş liste."""
        from reymen.hafiza.hafiza import AltAjanHafiza
        with patch("reymen.hafiza.hafiza.HAFIZA_DIZINI", tmp_path / ".alt_ajan_hafiza"):
            hafiza = AltAjanHafiza()
            assert hafiza.task_listele() == []


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 4 — Context Compression (arama_sirala + mesaj_ara tarih aralığı)
# ════════════════════════════════════════════════════════════════════════════

class TestTarihAraligi:
    """_tarih_araligi_coz: tarih format çözümleyici."""

    def test_none_donar(self):
        """None → (None, None)."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        sonuc = AdvancedSessionStorage._tarih_araligi_coz(None)
        assert sonuc == (None, None)

    def test_bos_string(self):
        """Boş string → (None, None)."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        assert AdvancedSessionStorage._tarih_araligi_coz("") == (None, None)

    def test_7g(self):
        """'7g' → son 7 gün."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        bas, bit = AdvancedSessionStorage._tarih_araligi_coz("7g")
        assert bas is not None
        assert bit is not None
        fark = bit - bas
        assert abs(fark - 7 * 86400) < 10  # ~7 gün

    def test_24s(self):
        """'24s' → son 24 saat."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        bas, bit = AdvancedSessionStorage._tarih_araligi_coz("24s")
        assert bas is not None
        fark = bit - bas
        assert abs(fark - 24 * 3600) < 10

    def test_bugun(self):
        """'bugun' → bugün başından şimdiye."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        bas, bit = AdvancedSessionStorage._tarih_araligi_coz("bugun")
        assert bas is not None
        assert bit is not None
        import datetime as _dt
        gun_basi = _dt.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        assert abs(bas - gun_basi.timestamp()) < 5

    def test_yyyy_mm_dd(self):
        """'2026-06-01..2026-06-30' aralığı."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        bas, bit = AdvancedSessionStorage._tarih_araligi_coz("2026-06-01..2026-06-30")
        assert bas is not None
        assert bit is not None
        assert bit > bas
        fark_gun = (bit - bas) / 86400
        assert 28 < fark_gun < 31  # ~30 gün

    def test_tuple_ver(self):
        """Direkt tuple → aynen döner."""
        from reymen.hafiza.session_db import AdvancedSessionStorage
        bas, bit = AdvancedSessionStorage._tarih_araligi_coz((100.0, 200.0))
        assert bas == 100.0
        assert bit == 200.0


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 5 — Vektörel Hafıza (vektorel_hafiza.py) — Embedding mock'lu
# ════════════════════════════════════════════════════════════════════════════

class TestVektorelHafizaYedek:
    """_BasitYedek: ChromaDB yokken TF-IDF benzeri yedek bellek."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Her test için taze yedek."""
        from reymen.hafiza.vektorel_hafiza import _BasitYedek
        self.yedek = _BasitYedek()

    def test_add_ve_query(self):
        """Ekleme ve sorgulama."""
        self.yedek.add(
            ids=["1", "2"],
            documents=["Python decorator nedir", "Flask API nasıl yazılır"],
            metadatas=[{"kategori": "python"}, {"kategori": "web"}],
        )
        sonuc = self.yedek.query(["Python decorator"], n_results=2)
        assert len(sonuc["documents"][0]) >= 1
        assert "decorator" in sonuc["documents"][0][0]

    def test_upsert_varolan_guncelle(self):
        """Upsert: varolan ID'yi günceller."""
        self.yedek.add(ids=["1"], documents=["eski"], metadatas=[{}])
        self.yedek.upsert(ids=["1"], documents=["yeni"], metadatas=[{"guncel": True}])

        sonuc = self.yedek.query(["yeni"])
        assert sonuc["documents"][0][0] == "yeni"

    def test_upsert_yeni_ekle(self):
        """Upsert: yeni ID ekler."""
        self.yedek.upsert(ids=["yeni1"], documents=["test"], metadatas=[{}])
        assert self.yedek.count() == 1

    def test_delete(self):
        """Silme."""
        self.yedek.add(ids=["1"], documents=["a"], metadatas=[{}])
        self.yedek.add(ids=["2"], documents=["b"], metadatas=[{}])
        self.yedek.delete(ids=["1"])

        assert self.yedek.count() == 1
        sonuc = self.yedek.query(["b"])
        assert len(sonuc["ids"][0]) == 1

    def test_count(self):
        """Sayma."""
        assert self.yedek.count() == 0
        self.yedek.add(ids=["1"], documents=["a"], metadatas=[{}])
        assert self.yedek.count() == 1

    def test_peek(self):
        """Peek: ilk N kaydı göster."""
        self.yedek.add(
            ids=["1", "2", "3"],
            documents=["a", "b", "c"],
            metadatas=[{}, {}, {}],
        )
        peek = self.yedek.peek(limit=2)
        assert len(peek["ids"]) == 2
        assert peek["ids"] == ["1", "2"]

    def test_bos_query(self):
        """Boş sorgu → boş sonuç."""
        sonuc = self.yedek.query(["yok"], n_results=3)
        assert len(sonuc["ids"][0]) == 0

    def test_benzerlik_0_ve_1_arasi(self):
        """_counter_cosine 0-1 arası döner."""
        from reymen.hafiza.vektorel_hafiza import _BasitYedek
        from collections import Counter
        skor = _BasitYedek._counter_cosine(
            Counter("merhaba dünya".split()),
            Counter("merhaba dünya".split()),
        )
        assert skor == pytest.approx(1.0, abs=0.001)

        skor2 = _BasitYedek._counter_cosine(
            Counter("merhaba dünya".split()),
            Counter("python kod".split()),
        )
        assert skor2 == 0.0

    def test_chroma_yoksa_yedek_kullan(self, tmp_path):
        """ChromaDB yoksa yedek oluşur."""
        from reymen.hafiza.vektorel_hafiza import vektorel_hafiza_sistemini_kur
        with patch("reymen.hafiza.vektorel_hafiza.CHROMA_AVAILABLE", False):
            sistem = vektorel_hafiza_sistemini_kur(str(tmp_path / "vektor"))
            assert sistem is not None
            assert hasattr(sistem, "query")


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 6 — GorevHafiza (gorev_hafiza.py) — Görev sonrası kayıt
# ════════════════════════════════════════════════════════════════════════════

class TestGorevHafiza:
    """gorev_sonrasi_hafiza: görev tamamlama → hafızaya kayıt."""

    def test_gorev_sonrasi_hafiza_basarili(self, tmp_path):
        """Başarılı görev → hafızaya kaydedilir."""
        from reymen.hafiza import gorev_hafiza

        # _hafizaya_kaydet'i mock'la (gerçek DB kurulumu olmadan)
        with patch.object(gorev_hafiza, "_HAFIZA_AKTIF", False):
            with patch.object(gorev_hafiza, "_hafiza", None):
                with patch.object(gorev_hafiza, "REYMEN_MEMORIES", tmp_path / ".ReYMeN" / "memories"):
                    sonuc = gorev_hafiza.gorev_sonrasi_hafiza(
                        task_id="test_task_1",
                        hedef="Kullanıcıya merhaba de",
                        sonuc={"basarili": True, "turlar": 2, "sure": 1.5, "yanit": "Merhaba!"},
                    )
                    assert sonuc["task_id"] == "test_task_1"
                    assert sonuc["hafiza"]["durum"] == "pasif"  # _HAFIZA_AKTIF=False
                    assert sonuc["sure_sn"] >= 0

    def test_gorev_sonrasi_hafiza_hata(self, tmp_path):
        """Hatalı görev → hata kaydedilir."""
        from reymen.hafiza import gorev_hafiza

        with patch.object(gorev_hafiza, "_HAFIZA_AKTIF", False):
            with patch.object(gorev_hafiza, "_hafiza", None):
                with patch.object(gorev_hafiza, "REYMEN_MEMORIES", tmp_path / ".ReYMeN" / "memories"):
                    sonuc = gorev_hafiza.gorev_sonrasi_hafiza(
                        task_id="test_hata",
                        hedef="başarısız görev",
                        sonuc={
                            "basarili": False,
                            "turlar": 3,
                            "sure": 5.0,
                            "hata": "ValueError: geçersiz parametre",
                        },
                    )
                    assert sonuc["task_id"] == "test_hata"
                    # Hata kaydı ozet'te görünmeli
                    assert "Hata" in sonuc["ozet"]

    def test_ozet_olustur_basarili(self):
        """Başarılı görev özeti."""
        from reymen.hafiza.gorev_hafiza import _ozet_olustur
        ozet = _ozet_olustur({
            "basarili": True,
            "sure_sn": 2.5,
            "tur_sayisi": 3,
            "hedef": "test görev",
        })
        assert "Başarılı" in ozet
        assert "test görev" in ozet
        assert "2.5" in ozet

    def test_ozet_olustur_hata(self):
        """Hatalı görev özeti."""
        from reymen.hafiza.gorev_hafiza import _ozet_olustur
        ozet = _ozet_olustur({
            "basarili": False,
            "sure_sn": 1.0,
            "tur_sayisi": 1,
            "hedef": "başarısız",
            "hata": "Timeout hatası",
        })
        assert "Hata" in ozet
        assert "Timeout" in ozet

    def test_guven_skoru_hesapla(self):
        """Güven skoru hesaplama."""
        from reymen.hafiza.gorev_hafiza import _guven_skoru_hesapla
        assert _guven_skoru_hesapla(3, 1) == 0.75
        assert _guven_skoru_hesapla(0, 0) == 0.5
        assert _guven_skoru_hesapla(10, 0) == 1.0

    def test_varsayilan_gecerlilik(self):
        """6 aylık varsayılan geçerlilik."""
        from reymen.hafiza.gorev_hafiza import _varsayilan_gecerlilik
        from datetime import datetime, timedelta
        tarih = _varsayilan_gecerlilik()
        assert len(tarih) == 10  # YYYY-MM-DD
        # ~180 gün sonrası
        alt_sinir = (datetime.now() + timedelta(days=179)).strftime("%Y-%m-%d")
        ust_sinir = (datetime.now() + timedelta(days=181)).strftime("%Y-%m-%d")
        assert alt_sinir <= tarih <= ust_sinir

    def test_dedup_kontrol(self):
        """Aynı içerik ikinci kez kaydedilmez."""
        from reymen.hafiza.gorev_hafiza import _dedup_kontrol, _dedup_hash_set

        # Her test öncesi set'i temizle
        _dedup_hash_set.clear()

        kayit1 = {"ozet": "benzersiz içerik 12345"}
        kayit2 = {"ozet": "benzersiz içerik 12345"}  # aynı

        assert _dedup_kontrol(kayit1, tur="icerik") is False  # ilk kez
        assert _dedup_kontrol(kayit2, tur="icerik") is True   # dedup

    def test_guncelle_son_kullanim(self):
        """Son kullanım güncelleme (hafiza pasifken sessiz atlar)."""
        from reymen.hafiza.gorev_hafiza import guncelle_son_kullanim
        # _HAFIZA_AKTIF=False → sessizce atlar, hata fırlatmaz
        guncelle_son_kullanim(1, kategori="test", basarili_mi=True)


# ════════════════════════════════════════════════════════════════════════════
# BÖLÜM 7 — Entegrasyon: Memory katmanı akış testi
# ════════════════════════════════════════════════════════════════════════════

class TestMemoryEntegrasyon:
    """SessionMemory → gorev_hafiza akışı (uçtan uca)."""

    def test_session_ve_gorev_entegrasyonu(self, ass_storage):
        """Session oluştur → mesaj ekle → session export → görev kaydı.

        Hafıza katmanının tüm aşamalarını tek bir akışta test eder.
        """
        # 1. Session oluştur
        sid = ass_storage.session_baslat(
            source="cli", model="deepseek",
            user_id="test_user",
            title="Test Konuşması",
        )
        assert sid

        # 2. Mesaj ekle
        ass_storage.mesaj_ekle(sid, "user", "Python decorator nedir?")
        ass_storage.mesaj_ekle(sid, "assistant", "Fonksiyon sarmalayıcıdır.")
        ass_storage.mesaj_ekle(sid, "user", "Örnek verir misin?")
        ass_storage.mesaj_ekle(sid, "assistant", "@decorator syntax'ı ile...")

        # 3. Session'ı bitir
        ass_storage.session_bitir(sid, end_reason="completed")

        # 4. Session doğrula
        session = ass_storage.session_bul(sid)
        assert session["message_count"] == 4
        assert session["end_reason"] == "completed"

        # 5. İstatistik
        ist = ass_storage.istatistik()
        assert ist["toplam_session"] >= 1

        # 6. Export
        export = ass_storage.session_export(sid, format="json")
        data = json.loads(export)
        assert len(data["messages"]) == 4
        assert data["session"]["title"] == "Test Konuşması"

        # 7. FTS5 arama
        sonuclar = ass_storage.session_search("decorator")
        assert len(sonuclar) >= 1
        assert sonuclar[0]["session_id"] == sid

    def test_sanal_session_flow(self, gelismis_hafiza):
        """GelismisHafiza ile tam akış: session → kayıt → ara → bitir."""
        gh = gelismis_hafiza

        # Session başlat
        gh.initialize("entegrasyon_test", baslik="Entegrasyon Testi")

        # Kayıtlar ekle
        gh.kaydet("kullanıcı giriş yaptı", "konusmalar", anahtar="login")
        gh.kaydet("sistem yanıt verdi: hoşgeldiniz", "konusmalar", anahtar="response")

        # FTS5 ara
        sonuc = gh.ara("giriş")
        assert len(sonuc) >= 1
        assert "giriş" in sonuc[0]["icerik"]

        # Koleksiyon filtreli ara
        sonuc2 = gh.ara("login", koleksiyon="konusmalar")
        assert len(sonuc2) >= 1

        # Session bitir
        gh.session_bitir(ozet="2 mesajlı entegrasyon testi")

        # Session doğrula
        c = gh._conn.cursor()
        row = c.execute(
            "SELECT mesaj_sayisi, ozet FROM sessions WHERE id='entegrasyon_test'"
        ).fetchone()
        assert row["mesaj_sayisi"] == 2
        assert "entegrasyon" in row["ozet"]
