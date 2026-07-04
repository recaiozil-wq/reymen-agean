"""test_beyin.py — Beyin testleri.

NOT: Beyin prompt caching (_CACHE_AKTIF) mock sonuclarini onbellege alir.
Ayni prompt+mesaj ile 2. cagri cache hit verir. Bu nedenle her test
farkli prompt kullanir.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from reymen.cereyan.beyin import Beyin, SaglayCiAdim, LLMYanitMeta


@pytest.fixture
def cfg():
    return {
        "default_provider": "deepseek",
        "default_model": "deepseek-v4-flash",
        "providers": {
            "deepseek": {
                "base_url": "https://api.deepseek.com",
                "api_key": "sk-test-key",
            },
        },
    }


@pytest.fixture
def msgs():
    return [{"role": "user", "content": "Merhaba"}]


# Manual mock/restore (patch.object thread+onbellek sorunu yaratir)
_ORIG = Beyin._cagir_ile_retry


def _mock_retry(ret=None, err=None):
    Beyin._cagir_ile_retry = MagicMock(return_value=ret, side_effect=err)


def _unmock():
    Beyin._cagir_ile_retry = _ORIG


class TestBeyinBaslatma:
    def test_provider_model(self, cfg):
        b = Beyin(config=cfg)
        assert b.provider == "deepseek" and b.model == "deepseek-v4-flash"

    def test_fallback_zinciri(self, cfg):
        assert isinstance(Beyin(config=cfg)._fallback_zinciri[0], SaglayCiAdim)

    def test_anahtar_bul(self, cfg):
        assert Beyin(config=cfg)._anahtar_bul("deepseek", {"api_key": "sk-x"}) == "sk-x"

    def test_varsayilan_model(self, cfg):
        assert Beyin(config=cfg)._varsayilan_model("x") == "default"

    def test_iptal(self, cfg):
        b = Beyin(config=cfg)
        b.iptal_et()
        assert b._iptal_olayi.is_set()
        b.sifirla()
        assert not b._iptal_olayi.is_set()


class TestDusun:
    """dusun() -> _cagir_ile_retry mock.

    ONEMLI: Her test FARKLI prompt kullanir!
    Beyin prompt caching (_CACHE_AKTIF) ayni prompt+mesaj ciftini
    onbellekten dondurur, bu da test izolasyonunu bozar.
    """

    def test_basarili(self, cfg, msgs):
        _mock_retry(ret="Merhaba! Ben ReYMeN")
        try:
            y = Beyin(config=cfg).dusun("P1_Sistem", msgs)
        finally:
            _unmock()
        assert "ReYMeN" in y

    def test_uzun(self, cfg, msgs):
        _mock_retry(ret="Evet. " * 50)
        try:
            y = Beyin(config=cfg).dusun("P2_UzunTest", msgs)
        finally:
            _unmock()
        assert len(y) > 100

    def test_bos(self, cfg, msgs):
        _mock_retry(ret="")
        try:
            y = Beyin(config=cfg).dusun("P3_BosTest", msgs)
        finally:
            _unmock()
        assert y == ""

    def test_500(self, cfg, msgs):
        _mock_retry(err=RuntimeError("500"))
        try:
            y = Beyin(config=cfg).dusun("P4_500Test", msgs)
        finally:
            _unmock()
        assert "Hata" in y

    def test_401(self, cfg, msgs):
        _mock_retry(err=RuntimeError("401"))
        try:
            y = Beyin(config=cfg).dusun("P5_401Test", msgs)
        finally:
            _unmock()
        assert "Hata" in y

    def test_402(self, cfg, msgs):
        _mock_retry(err=RuntimeError("402"))
        try:
            y = Beyin(config=cfg).dusun("P6_402Test", msgs)
        finally:
            _unmock()
        assert "Hata" in y

    def test_429(self, cfg, msgs):
        _mock_retry(err=RuntimeError("429"))
        try:
            y = Beyin(config=cfg).dusun("P7_429Test", msgs)
        finally:
            _unmock()
        assert "Hata" in y

    def test_timeout(self, cfg, msgs):
        _mock_retry(err=RuntimeError("timeout"))
        try:
            y = Beyin(config=cfg).dusun("P8_TimeoutTest", msgs)
        finally:
            _unmock()
        assert "Hata" in y


class TestCagir:
    """_cagir dispatcher (thread'siz, dogrudan)."""

    def test_openai_uyumlu(self, cfg, msgs):
        with patch.object(Beyin, "_cagir_openai_uyumlu", return_value="OK"):
            r = Beyin(config=cfg)._cagir(
                Beyin(config=cfg)._fallback_zinciri[0], "S", msgs
            )
        assert r.metin == "OK"

    def test_lmstudio(self, cfg, msgs):
        with patch.object(Beyin, "_cagir_lmstudio", return_value="LM"):
            adim = SaglayCiAdim("lmstudio", "m", "http://localhost:1234", "")
            r = Beyin(config=cfg)._cagir(adim, "S", msgs)
        assert r.metin == "LM"


class TestUretV2:
    def test_basarili(self, cfg, msgs):
        with patch.object(
            Beyin,
            "_cagir_openai_uyumlu_v2",
            return_value={
                "role": "assistant",
                "content": "Selam!",
                "tool_calls": [],
            },
        ):
            assert Beyin(config=cfg).uret_v2("S", msgs)["content"] == "Selam!"

    def test_tools(self, cfg, msgs):
        mock_ret = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "HESAPLA", "arguments": "{}"},
                }
            ],
        }
        with patch.object(Beyin, "_cagir_openai_uyumlu_v2", return_value=mock_ret):
            r = Beyin(config=cfg).uret_v2("S", msgs, tools=[{}])
        assert len(r["tool_calls"]) == 1

    def test_uret_alias(self, cfg, msgs):
        _mock_retry(ret="Alias")
        try:
            r = Beyin(config=cfg).uret("P9_AliasTest", msgs)
        finally:
            _unmock()
        assert r == "Alias"


class TestRateLimit:
    def test_429(self, cfg):
        import requests as r

        mr = MagicMock()
        mr.status_code = 429
        assert Beyin(config=cfg)._rate_limit_mi(r.HTTPError(response=mr))

    def test_500_degil(self, cfg):
        import requests as r

        mr = MagicMock()
        mr.status_code = 500
        assert not Beyin(config=cfg)._rate_limit_mi(r.HTTPError(response=mr))

    def test_fc_destek(self, cfg):
        assert Beyin(config=cfg).fc_destekleniyor()
