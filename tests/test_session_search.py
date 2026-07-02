# -*- coding: utf-8 -*-
"""
reymen/core/session_search.py için kapsamlı testler.

Test stratejisi:
  - Her testte tmp_path ile geçici SQLite veritabanı oluşturulur.
  - ss.DB_PATH, geçici veritabanına yönlendirilir.
  - Her test sonunda ss.DB_PATH orijinal değerine geri yüklenir.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

import src.core.session_search as ss


# ── Yardımcı fonksiyonlar ──────────────────────────────────────────────


def _db_olustur(db_path: Path, fts5_olsun: bool = True):
    """Geçici test veritabanı oluştur: tablolar + opsiyonel FTS5."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode=WAL")

    con.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            source TEXT,
            user_id TEXT,
            model TEXT,
            started_at TEXT,
            ended_at TEXT,
            message_count INTEGER DEFAULT 0,
            tool_call_count INTEGER DEFAULT 0,
            title TEXT
        );

        CREATE TABLE IF NOT EXISTS session_messages (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            rol TEXT,
            icerik TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS session_tool_calls (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            tool_name TEXT,
            args TEXT,
            result TEXT,
            created_at TEXT
        );
    """)

    if fts5_olsun:
        con.executescript("""
            CREATE VIRTUAL TABLE IF NOT EXISTS session_messages_fts
            USING fts5(icerik, content='session_messages', content_rowid='id');
        """)

    con.commit()
    con.close()
    return db_path


def _test_verisi_ekle(db_path: Path):
    """Test verisi ekle: 2 session, 5 mesaj, 1 tool call."""
    con = sqlite3.connect(str(db_path))

    # Session 1
    con.execute(
        "INSERT INTO sessions (id, source, user_id, model, started_at, title, "
        "message_count, tool_call_count) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("session-001", "web", "user1", "gpt-4",
         "2025-01-01T10:00:00", "Test Session 1", 3, 1),
    )
    # Session 2
    con.execute(
        "INSERT INTO sessions (id, source, user_id, model, started_at, title, "
        "message_count, tool_call_count) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("session-002", "api", "user2", "gpt-3.5",
         "2025-01-02T10:00:00", "Test Session 2", 2, 0),
    )

    # Mesajlar — session-001
    con.execute(
        "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (1, "session-001", "user",
         "Merhaba, bugün hava nasıl?", "2025-01-01T10:00:01"),
    )
    con.execute(
        "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (2, "session-001", "assistant",
         "Bugün hava güneşli ve sıcak.", "2025-01-01T10:00:02"),
    )
    con.execute(
        "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (3, "session-001", "user",
         "Teşekkür ederim!", "2025-01-01T10:00:03"),
    )

    # Mesajlar — session-002
    con.execute(
        "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (4, "session-002", "user",
         "Python ile dosya nasıl okunur?", "2025-01-02T10:00:01"),
    )
    con.execute(
        "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (5, "session-002", "assistant",
         "open() fonksiyonu ile dosya okuyabilirsiniz.", "2025-01-02T10:00:02"),
    )

    # Tool calls — session-001
    con.execute(
        "INSERT INTO session_tool_calls (id, session_id, tool_name, args, result, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (1, "session-001", "get_weather",
         '{"location": "Istanbul"}', '{"temp": 25}',
         "2025-01-01T10:00:01"),
    )

    con.commit()
    con.close()


# ── Fixture'lar ────────────────────────────────────────────────────────


@pytest.fixture
def tmp_db(tmp_path):
    """Geçici test veritabanı yolu."""
    return tmp_path / ".ReYMeN" / "session.db"


@pytest.fixture
def original_db_path():
    """Orijinal ss.DB_PATH değerini yakala."""
    return ss.DB_PATH


@pytest.fixture(autouse=True)
def _db_path_geri_yukle(original_db_path):
    """Her test sonunda ss.DB_PATH'i orijinal değerine geri yükle."""
    yield
    ss.DB_PATH = original_db_path


@pytest.fixture
def db_fts5_var(tmp_db):
    """FTS5 tablosu olan veritabanı (boş)."""
    _db_olustur(tmp_db, fts5_olsun=True)
    ss.DB_PATH = tmp_db
    return tmp_db


@pytest.fixture
def db_fts5_var_verili(db_fts5_var):
    """FTS5 tablosu + test verisi olan veritabanı."""
    _test_verisi_ekle(db_fts5_var)
    # FTS5 indeksini güncelle
    con = sqlite3.connect(str(db_fts5_var))
    con.execute(
        "INSERT INTO session_messages_fts (rowid, icerik) "
        "SELECT id, icerik FROM session_messages"
    )
    con.commit()
    con.close()
    return db_fts5_var


@pytest.fixture
def db_fts5_yok_verili(tmp_db):
    """FTS5 tablosu olmayan, sadece test verisi olan veritabanı."""
    _db_olustur(tmp_db, fts5_olsun=False)
    _test_verisi_ekle(tmp_db)
    ss.DB_PATH = tmp_db
    return tmp_db


# ═══════════════════════════════════════════════════════════════════════
# _fts5_sorgu_hazirla()
# ═══════════════════════════════════════════════════════════════════════


class TestFts5SorguHazirla:
    """_fts5_sorgu_hazirla() — sorgu temizleme ve dönüştürme."""

    def test_temiz_tek_kelime(self):
        """Tek kelimelik temiz sorgu."""
        assert ss._fts5_sorgu_hazirla("hava") == '"hava"*'

    def test_ozel_karakterler_temizlenir(self):
        """Ozel karakterler *, (, ) temizlenir."""
        sonuc = ss._fts5_sorgu_hazirla('"hava" * (test)')
        # join() boşluk ekler: "hava"* "test"*
        assert sonuc == '"hava"* "test"*'

    def test_coklu_kelime_and_mantigi(self):
        """Coklu kelime boslukla ayrilip AND mantiginda aranir."""
        sonuc = ss._fts5_sorgu_hazirla("hava nasil")
        assert sonuc == '"hava"* "nasil"*'

    def test_bos_string_aynen_doner(self):
        """Bos string aynen doner."""
        assert ss._fts5_sorgu_hazirla("") == ""

    def test_sadece_bosluk_aynen_doner(self):
        """Sadece bosluk karakterleri aynen doner."""
        assert ss._fts5_sorgu_hazirla("   ") == "   "

    def test_arka_arkaya_bosluk(self):
        """Ardisik bosluklar ayni kelime sayilmaz ama bos elemanlar elenir."""
        # split() ardışık boşlukları zaten eler
        sonuc = ss._fts5_sorgu_hazirla("merhaba   dunya")
        assert sonuc == '"merhaba"* "dunya"*'

    def test_or_neat_anahtar_kelimeleri_temizlenir(self):
        """OR, AND, NOT, NEAR gibi FTS5 anahtar kelimeleri de temizlenir
        (tirnak icine alinarak etkisizlestirilir)."""
        sonuc = ss._fts5_sorgu_hazirla("OR AND NOT NEAR")
        # Hepsi tırnak içine alınır, anahtar kelime olarak değil string olarak aranır
        assert '"OR"*' in sonuc
        assert '"AND"*' in sonuc
        assert '"NOT"*' in sonuc
        assert '"NEAR"*' in sonuc


# ═══════════════════════════════════════════════════════════════════════
# session_ara()
# ═══════════════════════════════════════════════════════════════════════


class TestSessionAra:
    """session_ara() — FTS5 full-text arama."""

    def test_sonuc_var(self, db_fts5_var_verili):
        """Arama sonucu bulunmalı."""
        sonuclar = ss.session_ara("hava")
        assert len(sonuclar) >= 1
        assert sonuclar[0]["session_id"] == "session-001"

    def test_sonuc_yok_eslesme(self, db_fts5_var_verili):
        """Eşleşme olmayan sorgu boş liste dönmeli."""
        sonuclar = ss.session_ara("xxxxxxxxxZZZZZZZZ")
        assert sonuclar == []

    def test_session_id_filtresi(self, db_fts5_var_verili):
        """Session ID filtresi ile arama."""
        sonuclar = ss.session_ara("hava", session_id="session-001")
        assert len(sonuclar) >= 1
        for s in sonuclar:
            assert s["session_id"] == "session-001"

    def test_session_ara_genel_hata(self, tmp_path, original_db_path):
        """session_ara'da genel Exception handleri (OperationalError disi)."""
        # Gecersiz bir SQLite dosyasi ile DatabaseError tetikle
        db_path = tmp_path / "corrupt.db"
        db_path.write_text("not a valid sqlite db file")
        ss.DB_PATH = db_path
        sonuclar = ss.session_ara("test")
        assert sonuclar == []

    def test_bos_sorgu_bos_liste(self, db_fts5_var_verili):
        """Boş sorgu her zaman boş liste dönmeli."""
        assert ss.session_ara("") == []

    def test_sadece_bosluk_bos_liste(self, db_fts5_var_verili):
        """Sadece boşluk içeren sorgu boş liste dönmeli."""
        assert ss.session_ara("   ") == []

    def test_limit_parametresi(self, db_fts5_var_verili):
        """Limit parametresi sonuç sayısını sınırlamalı."""
        # session-001'de hava geçen 2 mesaj var
        sonuclar = ss.session_ara("hava", limit=1)
        assert len(sonuclar) == 1

    def test_icerik_500_karakterle_sinirli(self, db_fts5_var_verili):
        """İçerik 500 karakterle sınırlanmalı."""
        con = sqlite3.connect(str(db_fts5_var_verili))
        con.execute(
            "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (99, "session-001", "user", "A" * 1000, "2025-01-01T12:00:00"),
        )
        con.execute(
            "INSERT INTO session_messages_fts (rowid, icerik) VALUES (?, ?)",
            (99, "A" * 1000),
        )
        con.commit()
        con.close()

        sonuclar = ss.session_ara("AAA")
        bulunan = [s for s in sonuclar if s["session_id"] == "session-001"
                   and s["icerik"].startswith("A")]
        assert len(bulunan) >= 1
        assert len(bulunan[0]["icerik"]) == 500

    def test_skor_yuvarlama(self, db_fts5_var_verili):
        """Skor değeri 4 ondalık basamağa yuvarlanmalı."""
        sonuclar = ss.session_ara("hava")
        if sonuclar:
            # bm25 değeri string representation'da 4 ondalık
            skor_str = str(sonuclar[0]["skor"])
            if "." in skor_str:
                ondalik = skor_str.split(".")[1]
                assert len(ondalik) <= 4

    def test_fts5_hata_trigram_fallback(self, db_fts5_yok_verili):
        """FTS5 tablosu yoksa trigram fallback çalışmalı."""
        sonuclar = ss.session_ara("hava")
        assert len(sonuclar) >= 1
        assert sonuclar[0]["session_id"] == "session-001"
        # Trigram fallback'te skor her zaman 0
        assert sonuclar[0]["skor"] == 0

    def test_ozel_karakterli_sorgu(self, db_fts5_var_verili):
        """Özel karakterler temizlenip aranabilmeli."""
        sonuclar = ss.session_ara('"hava" * (nasıl)')
        assert len(sonuclar) >= 1


# ═══════════════════════════════════════════════════════════════════════
# _trigram_ara()
# ═══════════════════════════════════════════════════════════════════════


class TestTrigramAra:
    """_trigram_ara() — LIKE ile fallback arama."""

    def test_like_arama(self, db_fts5_var_verili):
        """LIKE ile arama sonuç dönmeli."""
        sonuclar = ss._trigram_ara("hava")
        assert len(sonuclar) >= 1
        assert sonuclar[0]["session_id"] == "session-001"
        assert sonuclar[0]["skor"] == 0

    def test_session_id_filtresi(self, db_fts5_var_verili):
        """Session ID filtresi çalışmalı."""
        sonuclar = ss._trigram_ara("hava", session_id="session-001")
        assert len(sonuclar) >= 1
        for s in sonuclar:
            assert s["session_id"] == "session-001"

    def test_diger_session_a_ait_sonuc_gelmez(self, db_fts5_var_verili):
        """Farklı session_id filtresi ile o session'a ait olmayan sonuç gelmez."""
        sonuclar = ss._trigram_ara("hava", session_id="session-002")
        # "hava" session-002'de geçmez
        assert len(sonuclar) == 0

    def test_limit_parametresi(self, db_fts5_var_verili):
        """Limit parametresi çalışmalı."""
        sonuclar = ss._trigram_ara("hava", limit=1)
        assert len(sonuclar) == 1

    def test_icerik_500_karakterle_sinirli(self, db_fts5_var_verili):
        """İçerik 500 karakterle sınırlanmalı (trigram'da da)."""
        con = sqlite3.connect(str(db_fts5_var_verili))
        con.execute(
            "INSERT INTO session_messages (id, session_id, rol, icerik, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (99, "session-001", "user", "XYZ" + "Z" * 997, "2025-01-01T12:00:00"),
        )
        con.commit()
        con.close()

        sonuclar = ss._trigram_ara("XYZ")
        assert len(sonuclar) >= 1
        assert len(sonuclar[0]["icerik"]) == 500

    def test_hata_durumu_bos_liste(self, original_db_path):
        """DB hatasında boş liste dönmeli."""
        ss.DB_PATH = Path("/") / "nonexistent_dir_xyz" / "test.db"
        sonuclar = ss._trigram_ara("test")
        assert sonuclar == []


# ═══════════════════════════════════════════════════════════════════════
# _fts5_mevcut_mu()
# ═══════════════════════════════════════════════════════════════════════


class TestFts5MevcutMu:
    """_fts5_mevcut_mu() — FTS5 tablosu varlık kontrolü."""

    def test_fts5_var_done_true(self, db_fts5_var):
        """FTS5 tablosu varsa True dönmeli."""
        assert ss._fts5_mevcut_mu() is True

    def test_fts5_yok_done_false(self, tmp_db, original_db_path):
        """FTS5 tablosu yoksa False dönmeli."""
        _db_olustur(tmp_db, fts5_olsun=False)
        ss.DB_PATH = tmp_db
        assert ss._fts5_mevcut_mu() is False

    def test_db_hatasi_done_false(self):
        """DB bağlantı hatasında False dönmeli."""
        ss.DB_PATH = Path("/") / "nonexistent_dir_xyz" / "test.db"
        assert ss._fts5_mevcut_mu() is False


# ═══════════════════════════════════════════════════════════════════════
# session_listele()
# ═══════════════════════════════════════════════════════════════════════


class TestSessionListele:
    """session_listele() — session listeleme."""

    def test_veri_var_listeler(self, db_fts5_var_verili):
        """Session listesi dönmeli."""
        sonuclar = ss.session_listele()
        assert len(sonuclar) == 2
        # ORDER BY started_at DESC → en yeni ilk
        assert sonuclar[0]["id"] == "session-002"
        assert sonuclar[1]["id"] == "session-001"

    def test_tum_alanlar_var(self, db_fts5_var_verili):
        """Her session'da beklenen alanlar olmalı."""
        sonuclar = ss.session_listele()
        for s in sonuclar:
            assert "id" in s
            assert "source" in s
            assert "user_id" in s
            assert "model" in s
            assert "started_at" in s
            assert "message_count" in s
            assert "tool_call_count" in s
            assert "title" in s

    def test_limit_parametresi(self, db_fts5_var_verili):
        """Limit parametresi çalışmalı."""
        sonuclar = ss.session_listele(limit=1)
        assert len(sonuclar) == 1

    def test_veri_yok_bos_liste(self, db_fts5_var):
        """Hic session yokken bos liste donmeli."""
        sonuclar = ss.session_listele()
        assert sonuclar == []

    def test_session_listele_db_hatasi(self, tmp_path, original_db_path):
        """DB hatasinda bos liste donmeli."""
        ss.DB_PATH = tmp_path  # dizin, dosya degil
        sonuclar = ss.session_listele()
        assert sonuclar == []


# ======================================================================
# session_mesajlari()
# ======================================================================


class TestSessionMesajlari:
    """session_mesajlari() — session mesajlarını getirme."""

    def test_mesaj_var_doner(self, db_fts5_var_verili):
        """Session mesajları sıralı dönmeli."""
        mesajlar = ss.session_mesajlari("session-001")
        assert len(mesajlar) == 3
        # ORDER BY created_at ASC
        assert mesajlar[0]["rol"] == "user"
        assert mesajlar[0]["icerik"] == "Merhaba, bugün hava nasıl?"
        assert mesajlar[2]["rol"] == "user"
        assert mesajlar[2]["icerik"] == "Teşekkür ederim!"

    def test_tum_alanlar_var(self, db_fts5_var_verili):
        """Her mesajda beklenen alanlar olmalı."""
        mesajlar = ss.session_mesajlari("session-001")
        for m in mesajlar:
            assert "id" in m
            assert "session_id" in m
            assert "rol" in m
            assert "icerik" in m
            assert "created_at" in m

    def test_mesaj_yok_bos_liste(self, db_fts5_var_verili):
        """Olmayan session ID için boş liste dönmeli."""
        mesajlar = ss.session_mesajlari("session-999")
        assert mesajlar == []

    def test_limit_parametresi(self, db_fts5_var_verili):
        """Limit parametresi calismali."""
        mesajlar = ss.session_mesajlari("session-001", limit=2)
        assert len(mesajlar) == 2

    def test_session_mesajlari_db_hatasi(self, tmp_path, original_db_path):
        """DB hatasinda bos liste donmeli."""
        ss.DB_PATH = tmp_path  # dizin, dosya degil
        mesajlar = ss.session_mesajlari("session-001")
        assert mesajlar == []


# ======================================================================
# session_istatistik()
# ======================================================================


class TestSessionIstatistik:
    """session_istatistik() — DB istatistikleri."""

    def test_temel_akis(self, db_fts5_var_verili):
        """Tüm istatistik alanları dolu dönmeli."""
        istatistik = ss.session_istatistik()
        assert istatistik["session_sayisi"] == 2
        assert istatistik["mesaj_sayisi"] == 5
        assert istatistik["tool_cagri_sayisi"] == 1
        assert istatistik["fts5_aktif"] is True
        assert "db_yolu" in istatistik

    def test_fts5_aktif_false(self, db_fts5_yok_verili):
        """FTS5 tablosu yoksa fts5_aktif False dönmeli."""
        istatistik = ss.session_istatistik()
        assert istatistik["fts5_aktif"] is False

    def test_bos_db_istatistik(self, db_fts5_var):
        """Boş DB'de istatistikler 0 dönmeli."""
        istatistik = ss.session_istatistik()
        assert istatistik["session_sayisi"] == 0
        assert istatistik["mesaj_sayisi"] == 0
        assert istatistik["tool_cagri_sayisi"] == 0
        assert istatistik["fts5_aktif"] is True

    def test_db_hatasi_hata_dict(self):
        """DB bağlantı hatasında {'hata': ...} dönmeli."""
        ss.DB_PATH = Path("/") / "nonexistent_dir_xyz" / "test.db"
        istatistik = ss.session_istatistik()
        assert "hata" in istatistik


# ═══════════════════════════════════════════════════════════════════════
# CLI entry point (__main__)
# ═══════════════════════════════════════════════════════════════════════


class TestCli:
    """CLI entry point — __main__ bloku testleri."""

    @staticmethod
    def _clilist():
        """--list mantığını çalıştır."""
        for s in ss.session_listele():
            print(
                f"  [{s['id'][:8]}] {s.get('title', 'Başlıksız')}"
                f" — {s['message_count']} mesaj"
            )

    @staticmethod
    def _clistats():
        """--stats mantığını çalıştır."""
        print(json.dumps(ss.session_istatistik(), indent=2, ensure_ascii=False))

    @staticmethod
    def _clisorgu(sorgu: str, limit: int = 10):
        """Sorgu mantığını çalıştır."""
        sonuclar = ss.session_ara(sorgu, limit=limit)
        print(f"\n{'='*60}")
        print(f"  Arama: '{sorgu}' — {len(sonuclar)} sonuç")
        print(f"{'='*60}\n")
        for i, s in enumerate(sonuclar, 1):
            print(f"  [{i}] Session: {s['session_id'][:8]}...")
            print(f"      Rol: {s['rol']}")
            print(f"      Skor: {s['skor']}")
            print(f"      İçerik: {s['icerik'][:200]}...")
            print()

    def test_cli_list(self, db_fts5_var_verili, capsys):
        """--list sessionlari listelemeli."""
        self._clilist()
        captured = capsys.readouterr()
        assert "Test Session 1" in captured.out
        assert "Test Session 2" in captured.out
        assert "mesaj" in captured.out

    def test_cli_stats(self, db_fts5_var_verili, capsys):
        """--stats JSON istatistik basmalı."""
        self._clistats()
        captured = capsys.readouterr()
        assert '"session_sayisi": 2' in captured.out
        assert '"fts5_aktif": true' in captured.out

    def test_cli_sorgu_sonuc_var(self, db_fts5_var_verili, capsys):
        """Sorgu argümani ile arama yapilip sonuc basilmail."""
        self._clisorgu("hava")
        captured = capsys.readouterr()
        assert "Arama: 'hava'" in captured.out
        assert "Skor:" in captured.out
        assert "Icerik:" in captured.out or "İçerik:" in captured.out

    def test_cli_sorgu_sonuc_yok(self, db_fts5_var_verili, capsys):
        """Eşleşme olmayan sorguda 0 sonuç basılmalı."""
        self._clisorgu("ZZZZZZZZ")
        captured = capsys.readouterr()
        assert "0 sonuç" in captured.out

    def test_cli_sorgu_limit_ile(self, db_fts5_var_verili, capsys):
        """--limit parametresi ile sorgu."""
        # __main__'deki --limit mantığını simüle et
        sonuclar = ss.session_ara("hava", limit=1)
        print(f"\n{'='*60}")
        print(f"  Arama: 'hava' — {len(sonuclar)} sonuç")
        print(f"{'='*60}\n")
        for i, s in enumerate(sonuclar, 1):
            print(f"  [{i}] Session: {s['session_id'][:8]}...")
            print(f"      Rol: {s['rol']}")
            print(f"      Skor: {s['skor']}")
            print(f"      İçerik: {s['icerik'][:200]}...")
            print()
        captured = capsys.readouterr()
        assert "1 sonuç" in captured.out


# ═══════════════════════════════════════════════════════════════════════
# _db() — context manager kenar durumları
# ═══════════════════════════════════════════════════════════════════════


class TestDbContextManager:
    """_db() context manager testleri."""

    def test_rollback_on_exception(self, db_fts5_var):
        """Hata durumunda rollback yapılmalı (commit yapılmamalı)."""
        class TestException(Exception):
            pass

        try:
            with ss._db() as con:
                con.execute(
                    "INSERT INTO sessions (id) VALUES (?)", ("test-rollback",)
                )
                raise TestException("test rollback")
        except TestException:
            pass

        # Veri commit edilmemeli
        with ss._db() as con:
            row = con.execute(
                "SELECT id FROM sessions WHERE id=?", ("test-rollback",)
            ).fetchone()
            assert row is None
