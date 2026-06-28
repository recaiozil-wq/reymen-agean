# -*- coding: utf-8 -*-
"""tests/test_session_db.py — AdvancedSessionStorage kapsamlı test paketi (35 test).

Kapsam:
  - Başlatma ve şema kurulumu
  - session_baslat / session_bitir yaşam döngüsü
  - mesaj_ekle ve tool_call_kaydet
  - token_guncelle ve maliyet_guncelle
  - Sorgulama: session_bul, session_ara, son_sessionlar
  - istatistik
  - Geriye uyumluluk: FTS5 ajan_gunlugu
  - Hata toleransı
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from session_db import AdvancedSessionStorage


@pytest.fixture()
def db(tmp_path):
    """Her test için temiz, geçici bir DB döner."""
    yol = str(tmp_path / "test.db")
    return AdvancedSessionStorage(db_yolu=yol)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 1 — Başlatma ve şema (5 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestBaslatma:
    def test_db_dosyasi_olusur(self, tmp_path):
        yol = str(tmp_path / "yeni.db")
        AdvancedSessionStorage(db_yolu=yol)
        assert os.path.exists(yol)

    def test_sessions_tablosu_var(self, db):
        conn = db._baglan()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_session_messages_tablosu_var(self, db):
        conn = db._baglan()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='session_messages'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_session_tool_calls_tablosu_var(self, db):
        conn = db._baglan()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='session_tool_calls'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1

    def test_ajan_gunlugu_fts_var(self, db):
        conn = db._baglan()
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ajan_gunlugu'"
        ).fetchall()
        conn.close()
        assert len(rows) == 1


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 2 — session_baslat (7 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestSessionBaslat:
    def test_session_id_string_doner(self, db):
        sid = db.session_baslat(source="test")
        assert isinstance(sid, str)
        assert len(sid) > 0

    def test_farkli_sessionlar_farkli_id(self, db):
        s1 = db.session_baslat(source="a")
        s2 = db.session_baslat(source="b")
        assert s1 != s2

    def test_source_kaydediliyor(self, db):
        sid = db.session_baslat(source="cli")
        row = db.session_bul(sid)
        assert row["source"] == "cli"

    def test_model_kaydediliyor(self, db):
        sid = db.session_baslat(source="test", model="deepseek-chat")
        row = db.session_bul(sid)
        assert row["model"] == "deepseek-chat"

    def test_user_id_kaydediliyor(self, db):
        sid = db.session_baslat(source="test", user_id="kullanici1")
        row = db.session_bul(sid)
        assert row["user_id"] == "kullanici1"

    def test_started_at_ayarlaniyor(self, db):
        sid = db.session_baslat(source="test")
        row = db.session_bul(sid)
        assert row["started_at"] > 0

    def test_parent_session_id_kaydediliyor(self, db):
        ana = db.session_baslat(source="parent")
        alt = db.session_baslat(source="child", parent_session_id=ana)
        row = db.session_bul(alt)
        assert row["parent_session_id"] == ana


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 3 — session_bitir (4 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestSessionBitir:
    def test_ended_at_ayarlaniyor(self, db):
        sid = db.session_baslat(source="test")
        db.session_bitir(sid, end_reason="completed")
        row = db.session_bul(sid)
        assert row["ended_at"] is not None

    def test_end_reason_kaydediliyor(self, db):
        sid = db.session_baslat(source="test")
        db.session_bitir(sid, end_reason="error")
        row = db.session_bul(sid)
        assert row["end_reason"] == "error"

    def test_yok_session_bitirme_hata_vermez(self, db):
        db.session_bitir("olmayan-id", end_reason="test")  # exception olmamalı

    def test_bitis_nedeni_none_olabilir(self, db):
        sid = db.session_baslat(source="test")
        db.session_bitir(sid)
        row = db.session_bul(sid)
        assert row["ended_at"] is not None


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 4 — mesaj_ekle (4 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestMesajEkle:
    def test_mesaj_ekleniyor(self, db):
        sid = db.session_baslat(source="test")
        db.mesaj_ekle(sid, "user", "Merhaba")
        row = db.session_bul(sid)
        assert row["message_count"] == 1

    def test_birden_fazla_mesaj(self, db):
        sid = db.session_baslat(source="test")
        db.mesaj_ekle(sid, "user", "soru")
        db.mesaj_ekle(sid, "assistant", "cevap")
        row = db.session_bul(sid)
        assert row["message_count"] == 2

    def test_farkli_roller(self, db):
        sid = db.session_baslat(source="test")
        for rol in ("user", "assistant", "system", "tool"):
            db.mesaj_ekle(sid, rol, f"{rol} mesaji")
        row = db.session_bul(sid)
        assert row["message_count"] == 4

    def test_bos_icerik_kabul_edilir(self, db):
        sid = db.session_baslat(source="test")
        db.mesaj_ekle(sid, "user", "")  # boş string


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 5 — tool_call_kaydet (3 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestToolCallKaydet:
    def test_tool_call_sayisi_artiyor(self, db):
        sid = db.session_baslat(source="test")
        db.tool_call_kaydet(sid, "dosya_yaz", {"path": "x.txt"}, "OK", 100)
        row = db.session_bul(sid)
        assert row["tool_call_count"] == 1

    def test_api_call_count_artiyor(self, db):
        sid = db.session_baslat(source="test")
        db.tool_call_kaydet(sid, "hesapla", {}, "42", 50)
        row = db.session_bul(sid)
        assert row["api_call_count"] >= 1

    def test_str_args_da_kabul_edilir(self, db):
        sid = db.session_baslat(source="test")
        db.tool_call_kaydet(sid, "arac", "parametre_string", "sonuc", 0)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 6 — token_guncelle ve maliyet_guncelle (4 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestTokenMaliyet:
    def test_token_guncelleme(self, db):
        sid = db.session_baslat(source="test")
        db.token_guncelle(sid, input_tokens=500, output_tokens=200)
        row = db.session_bul(sid)
        assert row["input_tokens"] == 500
        assert row["output_tokens"] == 200

    def test_token_kumülatif(self, db):
        sid = db.session_baslat(source="test")
        db.token_guncelle(sid, input_tokens=100)
        db.token_guncelle(sid, input_tokens=150)
        row = db.session_bul(sid)
        assert row["input_tokens"] == 250

    def test_maliyet_guncelleme(self, db):
        sid = db.session_baslat(source="test")
        db.maliyet_guncelle(sid, estimated_cost=0.00042, cost_status="estimated")
        row = db.session_bul(sid)
        assert row["cost_status"] == "estimated"
        assert row["estimated_cost_usd"] == pytest.approx(0.00042, rel=1e-3)

    def test_cache_token_guncelleme(self, db):
        sid = db.session_baslat(source="test")
        db.token_guncelle(sid, cache_read_tokens=50, cache_write_tokens=30)
        row = db.session_bul(sid)
        assert row["cache_read_tokens"] == 50
        assert row["cache_write_tokens"] == 30


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 7 — Sorgulama (5 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestSorgulama:
    def test_session_bul_bos_dict_olmayan(self, db):
        sid = db.session_baslat(source="test")
        row = db.session_bul(sid)
        assert isinstance(row, dict)
        assert row.get("id") == sid

    def test_session_bul_olmayan_id(self, db):
        row = db.session_bul("olmayan-uuid")
        assert row == {}

    def test_son_sessionlar_liste_doner(self, db):
        db.session_baslat(source="cli")
        db.session_baslat(source="cli")
        result = db.son_sessionlar(limit=5)
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_son_sessionlar_source_filtre(self, db):
        db.session_baslat(source="cli")
        db.session_baslat(source="api")
        result = db.son_sessionlar(source="cli", limit=10)
        assert all(r["source"] == "cli" for r in result)

    def test_session_ara_liste_doner(self, db):
        sid = db.session_baslat(source="test", title="arama-testi")
        result = db.session_ara("arama-testi", limit=5)
        assert isinstance(result, list)


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 8 — İstatistik (2 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestIstatistik:
    def test_istatistik_dict_doner(self, db):
        stats = db.istatistik()
        assert isinstance(stats, dict)

    def test_istatistik_toplam_session_sayilir(self, db):
        db.session_baslat(source="a")
        db.session_baslat(source="b")
        stats = db.istatistik()
        assert stats.get("toplam_session", 0) >= 2


# ══════════════════════════════════════════════════════════════════════════════
# GRUP 9 — FTS ajan_gunlugu geriye uyumluluk (3 test)
# ══════════════════════════════════════════════════════════════════════════════

class TestAjanGunlugu:
    def test_gunluge_yaz_crash_etmez(self, db):
        db.gunluge_yaz("hedef", "DOSYA_YAZ", "TAMAM")

    def test_ara_liste_doner(self, db):
        db.gunluge_yaz("hedef", "ARAC_CALISTIR", "sonuc")
        result = db.ara("hedef")
        assert isinstance(result, list)

    def test_hata_ozeti_cek_dict_doner(self, db):
        db.gunluge_yaz("h", "ARAC", "[Hata]: bağlantı koptu")
        ozet = db.hata_ozeti_cek(son_n=10)
        assert isinstance(ozet, dict)
        assert "hata_sayisi" in ozet
