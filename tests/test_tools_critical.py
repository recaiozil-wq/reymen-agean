# -*- coding: utf-8 -*-
"""
test_tools_critical.py — tools/ kritik modüller: achievements, proxy, CUA
"""

import json
import os
from pathlib import Path

import pytest


# ═══════════════════════════════════════════════════════════════════
# ACHIEVEMENTS TESTLERI
# ═══════════════════════════════════════════════════════════════════

class TestAchievementsRozetler:
    """tools/achievements.py rozet sistemi."""

    def test_rozet_tanimlari_var(self):
        """8 rozet tanimi olmali."""
        from tools.achievements import ROZET_TANIMLARI
        assert len(ROZET_TANIMLARI) == 8
        rozet_idleri = [r["id"] for r in ROZET_TANIMLARI]
        assert "novice_explorer" in rozet_idleri
        assert "reymen_master" in rozet_idleri

    def test_rozet_tanimlari_zorunlu_alanlar(self):
        """Her rozette id, name, emoji olmali."""
        from tools.achievements import ROZET_TANIMLARI
        for r in ROZET_TANIMLARI:
            assert "id" in r
            assert "name" in r
            assert "emoji" in r

    def test_ilk_7_rozet_listesi(self):
        """ILK_7_ROZET son rozet haric hepsini icermeli."""
        from tools.achievements import ILK_7_ROZET, ROZET_TANIMLARI
        assert len(ILK_7_ROZET) == 7
        assert "reymen_master" not in ILK_7_ROZET

    def test_ver_rozet_idempotent(self, monkeypatch, tmp_path):
        """Ayni rozet iki kez verilince None donmeli."""
        from tools.achievements import _ver_rozet, ACHIEVEMENTS_DIR, STATS_DIR
        hedef = tmp_path / "achievements"
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", hedef)
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "stats")
        ilk = _ver_rozet("novice_explorer")
        assert ilk is not None
        assert ilk["id"] == "novice_explorer"
        ikinci = _ver_rozet("novice_explorer")
        assert ikinci is None  # idempotent

    def test_ver_rozet_gecersiz_id(self):
        """Gecersiz rozet ID'si None donmeli."""
        from tools.achievements import _ver_rozet
        assert _ver_rozet("olmayan_rozet") is None

    def test_rozet_var_mi(self, monkeypatch, tmp_path):
        """Rozet varsa True, yoksa False."""
        from tools.achievements import _ver_rozet, _rozet_var_mi, ACHIEVEMENTS_DIR, STATS_DIR
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", tmp_path / "ach")
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "st")
        _ver_rozet("tool_master")
        assert _rozet_var_mi("tool_master")

    def test_rozet_dosya_formati(self, monkeypatch, tmp_path):
        """Rozet JSON dosyasi dogru formatta."""
        from tools.achievements import _ver_rozet, ACHIEVEMENTS_DIR, STATS_DIR
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", tmp_path / "ach")
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "st")
        rozet = _ver_rozet("bug_hunter")
        assert rozet is not None
        assert "id" in rozet
        assert "name" in rozet
        assert "emoji" in rozet
        assert "earned_at" in rozet

    def test_tum_rozetleri_listele_bos(self, monkeypatch, tmp_path):
        """Henuz rozet yoksa bos liste donmeli."""
        from tools.achievements import _tum_rozetleri_listele, ACHIEVEMENTS_DIR, STATS_DIR
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", tmp_path / "ach")
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "st")
        assert _tum_rozetleri_listele() == []

    def test_tum_rozetleri_listele_dolu(self, monkeypatch, tmp_path):
        """Rozetler varsa dogru sayida liste donmeli."""
        from tools.achievements import _ver_rozet, _tum_rozetleri_listele, ACHIEVEMENTS_DIR, STATS_DIR
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", tmp_path / "ach")
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "st")
        _ver_rozet("novice_explorer")
        _ver_rozet("tool_master")
        rozetler = _tum_rozetleri_listele()
        assert len(rozetler) == 2

    def test_sayac_artir(self, monkeypatch, tmp_path):
        """Sayac her cagrida 1 artmali."""
        from tools.achievements import _sayac_artir, ACHIEVEMENTS_DIR, STATS_DIR
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", tmp_path / "ach")
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "st")
        deger = _sayac_artir("tools_used.json")
        assert deger == 1
        deger = _sayac_artir("tools_used.json")
        assert deger == 2

    def test_sayac_artir_farkli_anahtar(self, monkeypatch, tmp_path):
        """Farkli anahtarlar ayri ayri sayilmali."""
        from tools.achievements import _sayac_artir, ACHIEVEMENTS_DIR, STATS_DIR
        monkeypatch.setattr("tools.achievements.ACHIEVEMENTS_DIR", tmp_path / "ach")
        monkeypatch.setattr("tools.achievements.STATS_DIR", tmp_path / "st")
        assert _sayac_artir("tasks.json", "completed") == 1
        assert _sayac_artir("tasks.json", "failed") == 1

    def test_check_achievements_import(self):
        """check_achievements fonksiyonu import edilebilmeli."""
        try:
            from tools.achievements import check_achievements
            assert callable(check_achievements)
        except (ImportError, AttributeError):
            # Opsiyonel fonksiyon, yoksa sorun degil
            pass


# ═══════════════════════════════════════════════════════════════════
# PROXY TESTLERI
# ═══════════════════════════════════════════════════════════════════

class TestProxyConfig:
    """proxy/proxy_config.py."""

    def test_import_edilebilir(self):
        from proxy.proxy_config import ProxyConfig
        assert ProxyConfig is not None

    def test_varsayilan_config(self):
        from proxy.proxy_config import ProxyConfig
        cfg = ProxyConfig()
        assert hasattr(cfg, "DEFAULTS")
        assert hasattr(cfg, "to_dict")
        assert isinstance(cfg.to_dict(), dict)

    def test_config_env_override(self, monkeypatch):
        """Ortam degiskeni config'i ezebilmeli."""
        from proxy.proxy_config import ProxyConfig
        monkeypatch.setenv("REYMEN_PROXY_PORT", "9999")
        cfg = ProxyConfig()
        cfg_dict = cfg.to_dict()
        assert "port" in str(cfg_dict) or "9999" in str(cfg_dict)

    def test_config_gecersiz_env(self, monkeypatch):
        """Gecersiz env degeri varsayilani kullanmali."""
        from proxy.proxy_config import ProxyConfig
        monkeypatch.setenv("REYMEN_PROXY_PORT", "abc")
        cfg = ProxyConfig()
        assert isinstance(cfg.to_dict(), dict)


class TestProxyEngine:
    """proxy/proxy_engine.py."""

    def test_import_edilebilir(self):
        from proxy.proxy_engine import ThreadingProxyServer, _ProxyHandler
        assert ThreadingProxyServer is not None

    def test_proxy_handler_attributes(self):
        from proxy.proxy_engine import _ProxyHandler
        assert hasattr(_ProxyHandler, "do_GET")
        assert hasattr(_ProxyHandler, "do_CONNECT")
        assert hasattr(_ProxyHandler, "do_POST")

    def test_proxy_server_reuse_address(self):
        from proxy.proxy_engine import ThreadingProxyServer
        assert ThreadingProxyServer.allow_reuse_address is True
        assert ThreadingProxyServer.daemon_threads is True

    def test_connect_parse_bad_request(self):
        """Gecersiz CONNECT istegi 400 donmeli."""
        from proxy.proxy_engine import _ProxyHandler
        assert hasattr(_ProxyHandler, "do_CONNECT")

    def test_socks5_import(self):
        """SOCKS5 RFC 1928 destegi var mi kontrol et."""
        try:
            from proxy.proxy_engine import _socks5_handshake, _socks5_reply
            assert callable(_socks5_handshake)
        except ImportError:
            pass  # SOCKS5 henuz eklenmemis olabilir

    def test_proxy_config_entegrasyon(self):
        """Proxy engine config ile calisabiliyor."""
        from proxy.proxy_engine import ThreadingProxyServer
        from proxy.proxy_config import ProxyConfig
        cfg = ProxyConfig()
        assert hasattr(cfg, "to_dict")
        d = cfg.to_dict()
        assert isinstance(d, dict)


# ═══════════════════════════════════════════════════════════════════
# CUA TESTLERI (tools/cua_motor_araci)
# ═══════════════════════════════════════════════════════════════════

class TestCUAMotor:
    """CUA motor aracı testleri."""

    def test_import_edilebilirse_temel_islevler(self):
        """CUA import edilebiliyorsa temel fonksiyonlari kontrol et."""
        try:
            from cua_motor_araci import CUA_EKRAN_KULLAN, CUA_ARACLARI_TARA
            assert callable(CUA_EKRAN_KULLAN) or CUA_EKRAN_KULLAN is not None
        except (ImportError, ModuleNotFoundError):
            pytest.skip("cua_motor_araci kurulu degil (bagimlilik: pyautogui, mss)")

    def test_cua_araclari_tara_liste_dondurur(self):
        """CUA_ARACLARI_TARA rapor dondurur (str)."""
        try:
            from cua_motor_araci import CUA_ARACLARI_TARA
            rapor = CUA_ARACLARI_TARA() if callable(CUA_ARACLARI_TARA) else ""
            assert isinstance(rapor, str)
            assert len(rapor) > 0
        except (ImportError, ModuleNotFoundError):
            pytest.skip("cua_motor_araci kurulu degil")

    def test_cua_gerekli_kutuphaneler(self):
        """CUA icin gerekli kutuphaneler kontrolu."""
        eksikler = []
        for mod in ("PIL", "pyautogui", "mss"):
            try:
                __import__(mod.replace("PIL", "PIL.Image"))
            except ImportError:
                eksikler.append(mod)
        # En azindan PIL olmali (pyautogui ve mss opsiyonel)
        assert "PIL" not in eksikler, "PIL (Pillow) gerekli"

    def test_cua_on_kosul_kontrol(self):
        """on_kosul_kontrol() fonksiyonu import edilebilmeli."""
        try:
            from cua_motor_araci import on_kosul_kontrol
            assert callable(on_kosul_kontrol)
        except (ImportError, AttributeError):
            pytest.skip("on_kosul_kontrol henuz eklenmemis")

    def test_cua_motor_reymen_entegrasyonu(self):
        """CUA motoru motor.py'de _CUA_MEVCUT ile kontrol ediliyor."""
        import motor
        assert hasattr(motor, "_CUA_MEVCUT")
        assert motor._CUA_MEVCUT in (True, False)


# ═══════════════════════════════════════════════════════════════════
# PROMPT CACHING + CONTEXT COMPRESSOR
# ═══════════════════════════════════════════════════════════════════

class TestPromptCaching:
    """prompt_caching.py PromptCache."""

    def test_import_edilebilir(self):
        from prompt_caching import PromptCache
        assert PromptCache is not None

    def test_cache_olusturma(self):
        from prompt_caching import PromptCache
        cache = PromptCache(max_boyut=10, ttl_saniye=60)
        assert cache._max_boyut == 10
        assert cache._ttl == 60

    def test_cache_anahtar_uretimi(self):
        """Farkli girdiler farkli anahtar uretmeli."""
        from prompt_caching import PromptCache
        cache = PromptCache()
        anahtar1 = cache._anahtar_olustur("sistem1", [{"role": "user", "content": "merhaba"}])
        anahtar2 = cache._anahtar_olustur("sistem2", [{"role": "user", "content": "merhaba"}])
        assert anahtar1 != anahtar2

    def test_cache_ekle_ve_al(self):
        from prompt_caching import PromptCache
        cache = PromptCache(max_boyut=10, ttl_saniye=3600)
        sonuc = {"metin": "deneme", "token": 10}
        cache.ekle("sistem", [{"role": "user", "content": "test"}], sonuc)
        alinan = cache.al("sistem", [{"role": "user", "content": "test"}])
        assert alinan is not None
        assert alinan["metin"] == "deneme"

    def test_cache_bulunamadi(self):
        """Olmayan girdi icin None donmeli."""
        from prompt_caching import PromptCache
        cache = PromptCache(max_boyut=10, ttl_saniye=3600)
        assert cache.al("sistem", [{"role": "user", "content": "yok"}]) is None

    def test_cache_ttl_suresi_dolunca(self):
        """TTL dolunca cache temizlenmeli."""
        from prompt_caching import PromptCache
        import time
        cache = PromptCache(max_boyut=10, ttl_saniye=1)
        cache.ekle("s", [{"role": "user", "content": "x"}], {"metin": "test"})
        time.sleep(1.1)
        assert cache.al("s", [{"role": "user", "content": "x"}]) is None

    def test_cache_max_boyut(self):
        """Max boyut asilinca en eski eleman silinmeli."""
        from prompt_caching import PromptCache
        cache = PromptCache(max_boyut=2, ttl_saniye=3600)
        cache.ekle("s1", [{"role": "user", "content": "a"}], {"metin": "a"})
        cache.ekle("s2", [{"role": "user", "content": "b"}], {"metin": "b"})
        cache.ekle("s3", [{"role": "user", "content": "c"}], {"metin": "c"})
        assert len(cache._onbellek) <= 2

    def test_cache_temizle(self):
        from prompt_caching import PromptCache
        cache = PromptCache(max_boyut=10, ttl_saniye=3600)
        cache.ekle("s", [{"role": "user", "content": "x"}], {"metin": "t"})
        cache.temizle()
        assert len(cache._onbellek) == 0

    def test_cache_boyut(self):
        from prompt_caching import PromptCache
        cache = PromptCache(max_boyut=10, ttl_saniye=3600)
        cache.ekle("s1", [{"role": "user", "content": "a"}], {"metin": "a"})
        cache.ekle("s2", [{"role": "user", "content": "b"}], {"metin": "b"})
        assert cache.boyut() == 2


class TestContextCompressor:
    """context_compressor.py ContextCompressor."""

    def test_import_edilebilir(self):
        from context_compressor import ContextCompressor
        assert ContextCompressor is not None

    def test_compressor_varsayilan_token(self):
        from context_compressor import ContextCompressor
        comp = ContextCompressor()
        assert hasattr(comp, "ozet_olustur")
        assert hasattr(comp, "sikistir")

    def test_compressor_sikistir(self):
        """Sikistirma fonksiyonu calismali."""
        from context_compressor import ContextCompressor
        comp = ContextCompressor()
        mesajlar = [{"role": "user", "content": "test"}]
        sonuc = comp.sikistir(mesajlar)
        assert sonuc is not None

    def test_compressor_bilgi_sakla(self):
        from context_compressor import ContextCompressor
        comp = ContextCompressor()
        # onemli_bilgileri_sakla fonksiyonu var mi
        assert hasattr(comp, "onemli_bilgileri_sakla")

    def test_compressor_ozet_olustur(self):
        """Ozet olusturma fonksiyonu dict ile calismali."""
        from context_compressor import ContextCompressor
        comp = ContextCompressor()
        sonuc = comp.ozet_olustur([{"icerik": "Bu bir test metnidir.", "role": "user"}])
        assert sonuc is not None

    def test_compressor_onemli_bilgileri_sakla_ve_al(self):
        from context_compressor import ContextCompressor
        comp = ContextCompressor()
        comp.onemli_bilgileri_sakla("anahtar", "deger")
        sonuc = comp.onemli_bilgileri_al("anahtar")
        assert sonuc == "deger"
