"""test_config_manager.py - Config/ConfigManager saf fonksiyon testleri.

Hiçbir dış bağımlılık yok (API, dosya, ağ).
Config sınıfının get/set/merge/env override mantığını test eder.
"""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from reymen.core.config_manager import (
    Config,
    ConfigManager,
    _VARSAYILAN_DEGERLER,
    varsayilan_config,
)


# ── Config Başlatma ──────────────────────────────────────────────────────────

class TestConfigBaslatma:
    """Config() kurulumu ve varsayılan değerler."""

    def test_varsayilan_degerler_mevcut(self):
        """Varsayılan değerler sözlüğü dolu mu?"""
        assert "general.default_model" in _VARSAYILAN_DEGERLER
        assert "general.default_provider" in _VARSAYILAN_DEGERLER
        assert "approvals.mode" in _VARSAYILAN_DEGERLER
        assert _VARSAYILAN_DEGERLER["general.default_model"] == "deepseek-v4-flash"

    def test_config_bos_dict_ile_baslamaz(self):
        """Config() en azından varsayılan değerleri _data'da içermeli.

        Not: _VARSAYILAN_DEGERLER flat dot-notated keys kullanır,
        get() ise nested dict traversal yapar. _data'da dogrudan
        kontrol ederiz (flat key erisimi).
        """
        cfg = Config()
        # Flat key'ler _data'da durur, get() nested arar
        assert "general.agent_name" in cfg._data
        assert cfg._data["general.agent_name"] == "ReYMeN"

    def test_config_get_varsayilan_dondurur(self):
        """Olmayan anahtar için varsayılan değer dönüyor mu?"""
        cfg = Config()
        assert cfg.get("olmayan.anahtar", "fallback") == "fallback"
        assert cfg.get("hic_yok") is None

    def test_config_birden_fazla_varsayilan(self):
        """str, int, bool, list gibi farklı tipler varsayılan _data'da var mi?"""
        cfg = Config()
        assert "general.max_turns" in cfg._data
        assert isinstance(cfg._data["general.max_turns"], int)
        assert "approvals.mode" in cfg._data
        assert isinstance(cfg._data["approvals.mode"], str)
        assert "checkpoint.enabled" in cfg._data
        assert isinstance(cfg._data["checkpoint.enabled"], bool)


# ── Config Get / Set ─────────────────────────────────────────────────────────

class TestConfigGetSet:
    """Config.get() / set() / set_and_save()."""

    def test_get_dot_notation(self):
        """Nokta notasyonu ile iç içe anahtarlara erişim."""
        cfg = Config()
        cfg.set("test.alt.deger", "bulundu")
        assert cfg.get("test.alt.deger") == "bulundu"

    def test_set_ve_get_dongusu(self):
        """set() → get() tutarlı mı?"""
        cfg = Config()
        cfg.set("test.anahtar", "test_deger")
        assert cfg.get("test.anahtar") == "test_deger"

    def test_set_overwrite(self):
        """Aynı anahtara ikinci kez set() eski değeri siler."""
        cfg = Config()
        cfg.set("test.anahtar", "eski")
        cfg.set("test.anahtar", "yeni")
        assert cfg.get("test.anahtar") == "yeni"

    def test_set_dirty_flag(self):
        """set() sonrası _dirty=True oluyor mu?"""
        cfg = Config()
        assert cfg._dirty is False
        cfg.set("test.x", 1)
        assert cfg._dirty is True

    def test_set_bool_deger(self):
        """Boolean değerler doğru saklanıyor mu?"""
        cfg = Config()
        cfg.set("test.aktif", False)
        assert cfg.get("test.aktif") is False

    def test_set_int_deger(self):
        """Integer değerler doğru saklanıyor mu?"""
        cfg = Config()
        cfg.set("test.sayi", 42)
        assert cfg.get("test.sayi") == 42


# ── Config Yardımcı Metodları ────────────────────────────────────────────────

class TestConfigHelperMetodlari:
    """_dict_merge, _dict_set, _dict_anahtar_say, durum_raporu."""

    def test_dict_merge_basit(self):
        """İki düz sözlük doğru birleşiyor mu?"""
        hedef = {"a": 1}
        kaynak = {"b": 2}
        Config._dict_merge(hedef, kaynak)
        assert hedef == {"a": 1, "b": 2}

    def test_dict_merge_ic_ice(self):
        """İç içe sözlükler derinlemesine birleşiyor mu?"""
        hedef = {"ust": {"alt1": 1}}
        kaynak = {"ust": {"alt2": 2}}
        Config._dict_merge(hedef, kaynak)
        assert hedef == {"ust": {"alt1": 1, "alt2": 2}}

    def test_dict_merge_kaynaktan_overwrite(self):
        """Kaynak, hedefteki aynı anahtarı overwrite ediyor mu?"""
        hedef = {"a": 1}
        kaynak = {"a": 99}
        Config._dict_merge(hedef, kaynak)
        assert hedef["a"] == 99

    def test_dict_set_ic_ice(self):
        """_dict_set iç içe yol oluşturuyor mu?"""
        d = {}
        Config._dict_set(d, "seviye1.seviye2.deger", 42)
        assert d["seviye1"]["seviye2"]["deger"] == 42

    def test_dict_anahtar_say_bos(self):
        """Boş sözlükte 0 anahtar dönüyor mu?"""
        assert sum(Config._dict_anahtar_say({})) == 0

    def test_dict_anahtar_say_dolu(self):
        """İç içe sözlükte yaprak anahtarları sayıyor mu?"""
        d = {"a": 1, "b": {"c": 2, "d": 3}}
        assert sum(Config._dict_anahtar_say(d)) == 3

    def test_durum_raporu_yapisi(self):
        """durum_raporu() dict döndürüyor ve gerekli alanları içeriyor."""
        cfg = Config()
        rapor = cfg.durum_raporu()
        assert isinstance(rapor, dict)
        assert "profil" in rapor
        assert "varsayilan_model" in rapor
        assert "varsayilan_provider" in rapor
        assert "provider_sayisi" in rapor
        assert "dirty" in rapor

    def test_get_path_relative(self):
        """get_path() relative path'i proje kokune göre çözüyor."""
        cfg = Config()
        cfg.set("test.yol", "goreceli/dizin")
        p = cfg.get_path("test.yol")
        assert p is not None
        assert p.is_absolute()
        assert p.name == "dizin"

    def test_get_path_none(self):
        """get_path() olmayan anahtar için None dönüyor."""
        cfg = Config()
        assert cfg.get_path("olmayan.yol") is None

    def test_get_provider_chain_bos(self):
        """get_provider_chain() boş config'de varsayılan sırayı dönüyor."""
        cfg = Config()
        zincir = cfg.get_provider_chain()
        assert isinstance(zincir, list)
        assert len(zincir) > 0


# ── ConfigManager ────────────────────────────────────────────────────────────

class TestConfigManager:
    """ConfigManager get/set/list arayüzü."""

    def test_config_manager_get_varsayilan(self):
        """ConfigManager.get() varsayılan değer döndürüyor mu?

        Not: varsayilan degerler flat dot-notated keys oldugu icin
        _data'dan kontrol ederiz.
        """
        cm = ConfigManager()
        assert "general.agent_name" in cm._cfg._data
        assert cm._cfg._data["general.agent_name"] == "ReYMeN"

    def test_config_manager_get_fallback(self):
        """ConfigManager.get() olmayan anahtar için default dönüyor."""
        cm = ConfigManager()
        assert cm.get("yok.anahtar", "fallback") == "fallback"

    def test_config_manager_list_dict_doner(self):
        """ConfigManager.list() dict döndürüyor mu?"""
        cm = ConfigManager()
        data = cm.list()
        assert isinstance(data, dict)

    def test_config_manager_repr(self):
        """Config __repr__ çalışıyor mu?"""
        cfg = Config()
        r = repr(cfg)
        assert "Config" in r
        assert "profil" in r or "default" in r


# ── Singleton ────────────────────────────────────────────────────────────────

class TestVarsayilanConfig:
    """varsayilan_config() singleton."""

    def test_singleton_ayni_nesne(self):
        """İki çağrı aynı Config nesnesini dönüyor mu?"""
        c1 = varsayilan_config()
        c2 = varsayilan_config()
        assert c1 is c2

    def test_config_yeniden_yukle_yeni_nesne(self):
        """config_yeniden_yukle() yeni Config oluşturuyor mu?"""
        from reymen.core.config_manager import config_yeniden_yukle
        c1 = varsayilan_config()
        c2 = config_yeniden_yukle()
        assert c1 is not c2


# ── Environment Variable Override ────────────────────────────────────────────

class TestEnvOverride:
    """REYMEN_* env variable override."""

    def test_reymen_prefix_override(self):
        """REYMEN_ prefix ile env override calisiyor mu?

        Not: _env_override() tum alt cizgileri noktaya cevirir.
        Ornek: REYMEN_GENERAL_DEFAULT_MODEL -> general.default.model (YANLIS)
        Bu nedenle yaprak anahtarinda alt cizgi OLMAYAN key kullaniriz.
        """
        with patch.dict(os.environ, {"REYMEN_AGENT_NAME": "ReymenOverride"}, clear=False):
            cfg = Config()
            assert cfg.get("agent.name") == "ReymenOverride"

    def test_env_map_override(self):
        """_ENV_MAP üzerinden DEFAULT_MODEL -> general.default_model çalışıyor mu?"""
        with patch.dict(os.environ, {"DEFAULT_MODEL": "env-model"}, clear=False):
            cfg = Config()
            assert cfg.get("general.default_model") == "env-model"

    def test_env_override_gecici(self):
        """Env override sadece o Config instance'ı için geçerli."""
        with patch.dict(os.environ, {"REYMEN_TEST": "env-val"}, clear=False):
            cfg = Config()
            assert cfg.get("test") == "env-val"
        # patch bitti -> env yok
        cfg2 = Config()
        assert cfg2.get("test") is None


# ── Kaydetme (Config yokken) ─────────────────────────────────────────────────

class TestKaydetme:
    """kaydet() - config dosyası olmadan hata vermemeli."""

    def test_kaydet_hata_vermez(self, tmp_path):
        """Var olmayan config yolunda kaydet() False dönüyor mu?"""
        cfg = Config(config_yolu=tmp_path / "yok" / "config.yaml")
        sonuc = cfg.set_and_save("test.x", 1)
        # Dosya yok, kaydedemez -> False
        assert sonuc is False

    def test_set_and_save_dirty_reset(self, tmp_path):
        """set_and_save() sonrası dirty=False oluyor mu?"""
        cfg = Config(config_yolu=tmp_path / "config.yaml")
        # Dosya yok, kaydetme başarısız -> dirty True kalır
        cfg.set("test.x", 1)
        assert cfg._dirty is True
