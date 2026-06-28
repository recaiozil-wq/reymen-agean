# -*- coding: utf-8 -*-
"""tests/test_session_context.py — SessionContext / SessionContextManager birim testleri."""
import sys
import time
from pathlib import Path
PROJE_KOK = Path(__file__).parent.parent
sys.path.insert(0, str(PROJE_KOK))
import pytest
from gateway.session_context import (
    SessionContext, SessionContextManager, baglam,
    get_session_env, set_session_vars, clear_session_vars,
    set_current_session_id, get_current_session_id,
)


class TestSessionContext:
    def test_create(self):
        ctx = SessionContext("telegram", "kanal_1", "user_abc", "Ahmet")
        assert ctx.platform == "telegram"
        assert ctx.kanal == "kanal_1"
        assert ctx.kullanici == "user_abc"
        assert ctx.kullanici_adi == "Ahmet"
        assert len(ctx.id) == 12

    def test_kullanici_adi_default(self):
        ctx = SessionContext("discord", "ch", "user123")
        assert ctx.kullanici_adi == "user123"

    def test_set_get(self):
        ctx = SessionContext("test", "ch", "u")
        ctx.set("anahtar", "deger")
        assert ctx.get("anahtar") == "deger"

    def test_get_default(self):
        ctx = SessionContext("test", "ch", "u")
        assert ctx.get("yok", "varsayilan") == "varsayilan"

    def test_sil(self):
        ctx = SessionContext("test", "ch", "u")
        ctx.set("x", "y")
        assert ctx.sil("x") is True
        assert ctx.get("x") is None

    def test_sil_nonexistent(self):
        ctx = SessionContext("test", "ch", "u")
        assert ctx.sil("yok") is False

    def test_veri_al(self):
        ctx = SessionContext("test", "ch", "u")
        ctx.set("a", 1)
        ctx.set("b", 2)
        data = ctx.veri_al()
        assert data == {"a": 1, "b": 2}

    def test_guncelle(self):
        ctx = SessionContext("test", "ch", "u")
        old = ctx.son_aktivite
        time.sleep(0.01)
        ctx.guncelle()
        assert ctx.son_aktivite > old

    def test_sure(self):
        ctx = SessionContext("test", "ch", "u")
        assert ctx.sure() >= 0

    def test_aktif_mi(self):
        ctx = SessionContext("test", "ch", "u")
        assert ctx.aktif_mi(timeout=300) is True
        # force old activity
        ctx.son_aktivite = 0
        assert ctx.aktif_mi(timeout=1) is False

    def test_ozet(self):
        ctx = SessionContext("telegram", "k1", "u1")
        ozet = ctx.ozet()
        assert ozet["platform"] == "telegram"
        assert ozet["kanal"] == "k1"
        assert ozet["kullanici"] == "u1"
        assert ozet["aktif"] is True


class TestSessionContextManager:
    def test_olustur(self):
        sm = SessionContextManager()
        ctx = sm.olustur("telegram", "ch1", "user1", "Ali")
        assert ctx.platform == "telegram"
        assert sm.sayi() == 1

    def test_get(self):
        sm = SessionContextManager()
        ctx = sm.olustur("t", "c", "u")
        assert sm.get(ctx.id) is ctx
        assert sm.get("nonexistent") is None

    def test_bul(self):
        sm = SessionContextManager()
        ctx = sm.olustur("platform_x", "ch", "user_x")
        found = sm.bul("platform_x", "user_x")
        assert found is ctx

    def test_bul_nonexistent(self):
        sm = SessionContextManager()
        assert sm.bul("yok", "yok") is None

    def test_platform_oturumlari(self):
        sm = SessionContextManager()
        sm.olustur("telegram", "ch1", "u1")
        sm.olustur("telegram", "ch2", "u2")
        sm.olustur("discord", "ch3", "u3")
        assert len(sm.platform_oturumlari("telegram")) == 2
        assert len(sm.platform_oturumlari("discord")) == 1

    def test_kullanici_oturumlari(self):
        sm = SessionContextManager()
        sm.olustur("t", "c1", "same_user")
        sm.olustur("d", "c2", "same_user")
        sm.olustur("t", "c3", "other_user")
        assert len(sm.kullanici_oturumlari("same_user")) == 2
        assert len(sm.kullanici_oturumlari("other_user")) == 1

    def test_sil(self):
        sm = SessionContextManager()
        ctx = sm.olustur("t", "c", "u")
        assert sm.sil(ctx.id) is True
        assert sm.sil(ctx.id) is False

    def test_temizle(self):
        sm = SessionContextManager()
        ctx = sm.olustur("t", "c", "u")
        ctx.son_aktivite = 0  # expired
        sm.temizle(max_sure=1)
        assert sm.sayi() == 0

    def test_liste(self):
        sm = SessionContextManager()
        sm.olustur("t", "c", "u")
        lst = sm.liste()
        assert len(lst) == 1
        assert lst[0]["platform"] == "t"

    def test_platform_dagilimi(self):
        sm = SessionContextManager()
        sm.olustur("t", "c1", "u1")
        sm.olustur("t", "c2", "u2")
        sm.olustur("d", "c3", "u3")
        dag = sm.platform_dagilimi()
        assert dag["t"] == 2
        assert dag["d"] == 1

    def test_ping(self):
        sm = SessionContextManager()
        sm.olustur("t", "c", "u")
        result = sm.ping()
        assert result["modul"] == "session_context"
        assert result["aktif_oturum"] == 1

    def test_send_message_by_id(self):
        sm = SessionContextManager()
        ctx = sm.olustur("t", "c", "u")
        result = sm.send_message("merhaba", ctx.id)
        assert "kaydedildi" in result
        assert ctx.get("son_mesaj") == "merhaba"

    def test_send_message_by_platform_user(self):
        sm = SessionContextManager()
        sm.olustur("t", "c", "u1")
        result = sm.send_message("merhaba", "t:u1")
        assert "kaydedildi" in result

    def test_send_message_not_found(self):
        sm = SessionContextManager()
        result = sm.send_message("merhaba", "yok")
        assert "bulunamadı" in result

    def test_global_baglam(self):
        assert isinstance(baglam, SessionContextManager)


class TestSessionContextVars:
    def test_get_set_clear(self):
        tokens = set_session_vars(platform="telegram", chat_id="123")
        assert get_session_env("ReYMeN_SESSION_PLATFORM") == "telegram"
        assert get_session_env("ReYMeN_SESSION_CHAT_ID") == "123"
        clear_session_vars(tokens)
        assert get_session_env("ReYMeN_SESSION_PLATFORM") == ""

    def test_set_session_vars_none(self):
        tokens = set_session_vars(platform=None)
        assert get_session_env("ReYMeN_SESSION_PLATFORM") == ""

    def test_set_current_session_id(self):
        set_current_session_id("sess_001")
        assert get_current_session_id() == "sess_001"
        set_current_session_id("")
        assert get_current_session_id() == ""
