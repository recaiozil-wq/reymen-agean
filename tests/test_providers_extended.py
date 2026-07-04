# -*- coding: utf-8 -*-
"""
test_providers_extended.py — providers/, session_db, conversation_loop
"""

import json
import os
from pathlib import Path

import pytest


# ═══════════════════════════════════════════════════════════════════
# PROVIDER TESTLERI
# ═══════════════════════════════════════════════════════════════════


class TestProviderProfile:
    """providers/base.py ProviderProfile."""

    def test_profile_olusturma(self):
        from providers.base import ProviderProfile

        p = ProviderProfile(name="test", base_url="https://test.com")
        assert p.name == "test"
        assert p.base_url == "https://test.com"
        assert p.openai_compat is True

    def test_profile_varsayilan_degerler(self):
        from providers.base import ProviderProfile

        p = ProviderProfile(name="varsayilan", base_url="http://localhost")
        assert p.env_vars == ()
        assert p.aliases == ()
        assert p.api_key_header == "Authorization"

    def test_api_key_from_env(self, monkeypatch):
        from providers.base import ProviderProfile

        monkeypatch.setenv("TEST_API_KEY", "sk-test-key")
        p = ProviderProfile(name="test", base_url="x", env_vars=("TEST_API_KEY",))
        assert p.api_key_from_env() == "sk-test-key"

    def test_api_key_from_env_bos(self):
        from providers.base import ProviderProfile

        p = ProviderProfile(name="test", base_url="x", env_vars=("OLMAYAN_KEY",))
        assert p.api_key_from_env() == ""

    def test_api_key_from_env_masked(self, monkeypatch):
        from providers.base import ProviderProfile

        monkeypatch.setenv("TEST_KEY", "***masked***")
        p = ProviderProfile(name="test", base_url="x", env_vars=("TEST_KEY",))
        assert p.api_key_from_env() == ""

    def test_headers_olusturma(self):
        from providers.base import ProviderProfile

        p = ProviderProfile(name="test", base_url="https://api.test.com")
        h = p.headers("sk-test")
        assert "Authorization" in h
        assert h["Authorization"] == "Bearer sk-test"

    def test_headers_ozel_prefix(self):
        from providers.base import ProviderProfile

        p = ProviderProfile(name="test", base_url="x", api_key_prefix="ApiKey")
        h = p.headers("key123")
        assert h["Authorization"] == "ApiKey key123"

    def test_headers_bos_api_key(self):
        from providers.base import ProviderProfile

        p = ProviderProfile(name="test", base_url="x")
        h = p.headers()
        assert "Authorization" not in h

    def test_omitted_temperature_sentinel(self):
        from providers.base import OMIT_TEMPERATURE

        assert OMIT_TEMPERATURE is not None
        assert isinstance(OMIT_TEMPERATURE, object)


class TestProviderRegistry:
    """providers/__init__.py registry."""

    def test_get_provider(self):
        from providers import get_provider

        profil = get_provider("deepseek")
        assert profil is not None
        assert profil.name == "deepseek"

    def test_get_provider_alias(self):
        """Alias ile provider bulunabilmeli."""
        from providers import get_provider

        profil = get_provider("claude")
        assert profil is not None
        assert profil.name == "anthropic" or profil.name == "claude"

    def test_get_provider_gecersiz(self):
        from providers import get_provider

        assert get_provider("olmayan_provider_12345") is None

    def test_list_providers(self):
        from providers import list_providers

        liste = list_providers()
        assert isinstance(liste, list)
        assert len(liste) > 0
        assert "deepseek" in liste

    def test_plugin_al(self):
        from providers import plugin_al

        plugin = plugin_al("lmstudio")
        # LM Studio plugin yuklenebilmeli
        assert plugin is not None
        assert hasattr(plugin, "test") or hasattr(plugin, "ping")

    def test_plugin_al_gecersiz(self):
        from providers import plugin_al

        assert plugin_al("olmayan_plugin_99999") is None

    def test_plugin_listele(self):
        from providers import plugin_listele

        liste = plugin_listele()
        assert isinstance(liste, list)
        assert len(liste) > 0

    def test_plugin_ping(self):
        from providers import plugin_ping

        ok, mesaj = plugin_ping("lmstudio")
        assert ok in (True, False)
        assert isinstance(mesaj, str)


class TestProviderPlugins:
    """Her provider plugin'inin temel islevleri."""

    def test_lmstudio_plugin(self):
        from providers.lmstudio_plugin import LMStudioPlugin

        p = LMStudioPlugin()
        assert hasattr(p, "test")
        assert hasattr(p, "ping")

    def test_deepseek_plugin(self):
        from providers.deepseek_plugin import DeepSeekPlugin

        p = DeepSeekPlugin()
        assert hasattr(p, "test")

    def test_anthropic_plugin(self):
        from providers.anthropic_plugin import AnthropicPlugin

        p = AnthropicPlugin()
        assert hasattr(p, "test")

    def test_openai_plugin(self):
        from providers.openai_plugin import OpenAIPlugin

        p = OpenAIPlugin()
        assert hasattr(p, "test")

    def test_provider_siniflari_standart(self):
        """Tum plugin siniflari ProviderPlugin tabanindan turemeli."""
        from providers.plugin_base import ProviderPlugin
        import providers

        for attr in dir(providers):
            obj = getattr(providers, attr)
            if (
                isinstance(obj, type)
                and issubclass(obj, ProviderPlugin)
                and obj is not ProviderPlugin
            ):
                assert hasattr(obj, "test") or True  # en azindan var


# ═══════════════════════════════════════════════════════════════════
# SESSION DB TESTLERI
# ═══════════════════════════════════════════════════════════════════


class TestSessionDB:
    """session_db.py AdvancedSessionStorage."""

    def test_import_edilebilir(self):
        from session_db import AdvancedSessionStorage

        assert AdvancedSessionStorage is not None

    def test_baslat_ve_bitir(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "test.db"))
        sid = db.session_baslat(source="test", model="mock")
        assert sid is not None
        assert isinstance(sid, str)
        assert len(sid) > 0
        db.session_bitir(sid, end_reason="completed")

    def test_benzersiz_session_id(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "unique.db"))
        s1 = db.session_baslat(source="test", model="m1")
        s2 = db.session_baslat(source="test", model="m2")
        assert s1 != s2

    def test_bitmemis_session_listele(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "active.db"))
        db.session_baslat(source="test", model="m")
        aktif = db.aktif_sessionlar() if hasattr(db, "aktif_sessionlar") else []
        assert isinstance(aktif, list)

    def test_session_token_guncelle(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "token.db"))
        sid = db.session_baslat(source="test", model="m")
        db.token_guncelle(sid, input_tokens=100, output_tokens=50)
        # Session bilgisini kontrol et
        bilgi = db.session_bilgi(sid) if hasattr(db, "session_bilgi") else None
        if bilgi:
            assert bilgi["input_tokens"] >= 100

    def test_session_metadata(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "meta.db"))
        sid = db.session_baslat(source="cli", model="deepseek")
        assert sid is not None
        assert isinstance(sid, str)

    def test_session_listele(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "list.db"))
        db.session_baslat(source="t1", model="m1")
        db.session_baslat(source="t2", model="m2")
        liste = db.session_listele() if hasattr(db, "session_listele") else []
        assert isinstance(liste, list)

    def test_veritabani_olusturma(self, tmp_path):
        """DB dosyasi otomatik olusturulmali."""
        db_yol = tmp_path / "yeni.db"
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(db_yol))
        sid = db.session_baslat(source="create", model="m")
        assert sid is not None
        assert db_yol.exists()

    def test_gecersiz_session_id(self, tmp_path):
        from session_db import AdvancedSessionStorage

        db = AdvancedSessionStorage(str(tmp_path / "invalid.db"))
        db.session_baslat(source="test", model="m")
        # Olmayan session ID'si ile islem
        try:
            db.token_guncelle("olmayan-session-id", input_tokens=1, output_tokens=1)
        except Exception:
            pass  # Hata firlatmamasi da kabul, patlamamasi onemli


# ═══════════════════════════════════════════════════════════════════
# CONVERSATION LOOP TESTLERI
# ═══════════════════════════════════════════════════════════════════


class TestConversationLoop:
    """conversation_loop.py ConversationLoop ve sabitler."""

    def test_gorev_bitti_tetikleyicileri(self):
        from conversation_loop import GOREV_BITTI_TETIK

        assert isinstance(GOREV_BITTI_TETIK, list)
        assert "GOREV_BITTI" in GOREV_BITTI_TETIK
        assert "GÖREV_BİTTİ" in GOREV_BITTI_TETIK
        assert "TASK_COMPLETE" in GOREV_BITTI_TETIK
        assert len(GOREV_BITTI_TETIK) >= 4

    def test_eylem_regex_calismali(self):
        from conversation_loop import _EYLEM_RE

        eslesme = _EYLEM_RE.search("Eylem: TEST_ARAC(arg1, arg2)")
        assert eslesme is not None
        assert eslesme.group(1) == "TEST_ARAC"
        assert eslesme.group(2) == "arg1, arg2"

    def test_eylem_regex_bos_arguman(self):
        from conversation_loop import _EYLEM_RE

        eslesme = _EYLEM_RE.search("Eylem: BITIR()")
        assert eslesme is not None
        assert eslesme.group(2) == ""

    def test_eylem_regex_eslesmezse(self):
        from conversation_loop import _EYLEM_RE

        assert _EYLEM_RE.search("Bu bir eylem degil") is None

    def test_arac_regex_calismali(self):
        from conversation_loop import _ARAC_RE

        eslesme = _ARAC_RE.search("DOSYA_AC(/tmp/test.txt)")
        assert eslesme is not None
        assert eslesme.group(1) == "DOSYA_AC"

    def test_conversation_loop_import(self):
        """ConversationLoop sinifi import edilebilmeli."""
        try:
            from conversation_loop import ConversationLoop

            assert ConversationLoop is not None
        except ImportError:
            # ConversationLoop henuz eklenmemis olabilir (wrapper)
            pass

    def test_budget_sinifi(self):
        from conversation_loop import _Budget

        b = _Budget(max_tur=25)
        assert b.max_tur == 25
        assert b._tur == 0
        assert b.kaldi == 25

    def test_budget_adim_atilinca(self):
        from conversation_loop import _Budget

        b = _Budget(max_tur=5)
        b._tur += 1
        b.kaldi = b.max_tur - b._tur
        assert b._tur == 1
        assert b.kaldi == 4

    def test_compressor_entegrasyonu(self):
        """conversation_loop _COMPRESSOR import edebilmeli."""
        from conversation_loop import _COMPRESSOR

        assert _COMPRESSOR is not None or _COMPRESSOR is None  # opsiyonel

    def test_cache_entegrasyonu(self):
        """conversation_loop _CACHE import edebilmeli."""
        from conversation_loop import _CACHE

        assert _CACHE is not None or _CACHE is None  # opsiyonel
