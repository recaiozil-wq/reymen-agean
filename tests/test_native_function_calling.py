# -*- coding: utf-8 -*-
"""tests/test_native_function_calling.py — Native function calling testleri.

Kapsar:
- beyin.uret_v2(): tools schema gönderimi, tool_calls parse
- beyin._cagir_openai_uyumlu_v2(): payload yapısı
- conversation_loop._motor_tools_schema_al(): schema üretimi
- _interruptible_api_call(): uret_v2 önceliği
"""

import json
import os
import sys
import types
from unittest.mock import MagicMock, patch, call

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Windows'ta paramiko→invoke→pty→tty.TCSAFLUSH zinciri kırık.
# Motor plugin yüklemesi sırasında tetikleniyor; sahte modüller ile önle.
for _mod in ("tty", "pty", "termios", "paramiko", "invoke", "fabric"):
    if _mod not in sys.modules:
        sys.modules[_mod] = MagicMock()


# ── Yardımcı sabitler ───────────────────────────────────────────────────────

SISTEM = "Sen yardımcı bir asistansın."
MESAJLAR = [{"role": "user", "content": "merhaba"}]
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "DOSYA_OKU",
            "description": "Dosya oku",
            "parameters": {
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": [],
            },
        },
    }
]


# ── beyin.uret_v2 testleri ───────────────────────────────────────────────────


class TestUretV2:
    @pytest.fixture
    def beyin(self):
        from beyin import Beyin

        b = Beyin({"provider": "deepseek", "model": "deepseek-chat", "api_key": "test"})
        return b

    def test_uret_v2_mevcutsa(self, beyin):
        assert hasattr(beyin, "uret_v2")

    def test_uret_v2_basarili_tool_calls(self, beyin, monkeypatch):
        """API'dan tool_calls gelmesi."""
        beklenen_yanit = {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "id": "tc_1",
                    "type": "function",
                    "function": {
                        "name": "DOSYA_OKU",
                        "arguments": '{"param": "test.txt"}',
                    },
                }
            ],
        }
        monkeypatch.setattr(
            beyin, "_cagir_openai_uyumlu_v2", lambda *a, **kw: beklenen_yanit
        )
        sonuc = beyin.uret_v2(SISTEM, MESAJLAR, tools=TOOLS_SCHEMA)
        assert sonuc["tool_calls"]
        assert sonuc["tool_calls"][0]["function"]["name"] == "DOSYA_OKU"

    def test_uret_v2_metin_yanit(self, beyin, monkeypatch):
        """API metin yanıtı döndürünce tool_calls boş."""
        beklenen = {"role": "assistant", "content": "Merhaba!", "tool_calls": []}
        monkeypatch.setattr(beyin, "_cagir_openai_uyumlu_v2", lambda *a, **kw: beklenen)
        sonuc = beyin.uret_v2(SISTEM, MESAJLAR, tools=TOOLS_SCHEMA)
        assert sonuc["content"] == "Merhaba!"
        assert sonuc["tool_calls"] == []

    def test_uret_v2_tools_none_fallback(self, beyin, monkeypatch):
        """tools=None → metin üret (dusun çağrılır)."""
        monkeypatch.setattr(beyin, "dusun", lambda s, m, **kw: "test yanıt")
        sonuc = beyin.uret_v2(SISTEM, MESAJLAR, tools=None)
        # tools=None olunca _cagir_openai_uyumlu_v2'ye gider ama tools boş
        # provider başarısız olursa dusun'a düşer → test sadece return type'ı doğrular
        assert isinstance(sonuc, dict)
        assert "content" in sonuc
        assert "tool_calls" in sonuc

    def test_uret_v2_hata_fallback(self, beyin, monkeypatch):
        """Tüm provider'lar başarısız → metin fallback."""
        monkeypatch.setattr(
            beyin,
            "_cagir_openai_uyumlu_v2",
            MagicMock(side_effect=Exception("API hatası")),
        )
        monkeypatch.setattr(beyin, "dusun", lambda *a, **kw: "fallback yanıt")
        sonuc = beyin.uret_v2(SISTEM, MESAJLAR, tools=TOOLS_SCHEMA)
        assert sonuc["content"] == "fallback yanıt"
        assert sonuc["tool_calls"] == []

    def test_uret_v2_dict_donuyor(self, beyin, monkeypatch):
        monkeypatch.setattr(
            beyin,
            "_cagir_openai_uyumlu_v2",
            lambda *a, **kw: {"role": "assistant", "content": "ok", "tool_calls": []},
        )
        sonuc = beyin.uret_v2(SISTEM, MESAJLAR, tools=TOOLS_SCHEMA)
        assert isinstance(sonuc, dict)
        assert "role" in sonuc


# ── _cagir_openai_uyumlu_v2 testleri ────────────────────────────────────────


class TestCagirOpenAIUyumluV2:
    @pytest.fixture
    def beyin(self):
        from beyin import Beyin

        return Beyin(
            {"provider": "deepseek", "model": "deepseek-chat", "api_key": "test"}
        )

    def test_payload_tools_gonderilir(self, beyin):
        """tools varsa payload'a eklenir, tool_choice='auto' olur."""
        gonderilen_payload = {}

        def mock_post(url, headers=None, json=None, timeout=None):
            gonderilen_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "ok", "tool_calls": None}}]
            }
            return mock_resp

        with patch("requests.post", mock_post):
            beyin._cagir_openai_uyumlu_v2(
                "https://api.example.com",
                "key",
                "model",
                SISTEM,
                MESAJLAR,
                tools=TOOLS_SCHEMA,
            )

        assert "tools" in gonderilen_payload
        assert gonderilen_payload["tool_choice"] == "auto"
        assert len(gonderilen_payload["tools"]) == 1

    def test_payload_tools_yok(self, beyin):
        """tools=None → payload'da tools yok."""
        gonderilen_payload = {}

        def mock_post(url, headers=None, json=None, timeout=None):
            gonderilen_payload.update(json)
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "ok", "tool_calls": None}}]
            }
            return mock_resp

        with patch("requests.post", mock_post):
            beyin._cagir_openai_uyumlu_v2(
                "https://api.example.com", "key", "model", SISTEM, MESAJLAR, tools=None
            )

        assert "tools" not in gonderilen_payload
        assert "tool_choice" not in gonderilen_payload

    def test_tool_calls_parse(self, beyin):
        """API tool_calls döndürünce doğru parse edilir."""
        tc = [
            {
                "id": "tc_1",
                "type": "function",
                "function": {"name": "DOSYA_OKU", "arguments": '{"param": "x.txt"}'},
            }
        ]

        def mock_post(url, headers=None, json=None, timeout=None):
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": None, "tool_calls": tc}}]
            }
            return mock_resp

        with patch("requests.post", mock_post):
            sonuc = beyin._cagir_openai_uyumlu_v2(
                "https://api.example.com",
                "key",
                "model",
                SISTEM,
                MESAJLAR,
                tools=TOOLS_SCHEMA,
            )

        assert sonuc["tool_calls"] == tc
        assert sonuc["content"] == ""

    def test_yanit_formati_dict(self, beyin):
        """Dönüş her zaman dict: role, content, tool_calls."""

        def mock_post(url, headers=None, json=None, timeout=None):
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {
                "choices": [{"message": {"content": "merhaba", "tool_calls": None}}]
            }
            return mock_resp

        with patch("requests.post", mock_post):
            sonuc = beyin._cagir_openai_uyumlu_v2(
                "https://api.example.com", "key", "model", SISTEM, MESAJLAR
            )
        assert sonuc["role"] == "assistant"
        assert sonuc["content"] == "merhaba"
        assert sonuc["tool_calls"] == []


# ── _motor_tools_schema_al testleri ─────────────────────────────────────────


class TestMotorToolsSchemaAl:
    def test_bos_motor(self):
        from conversation_loop import _motor_tools_schema_al

        motor = MagicMock()
        motor._plugin_araclar = {}
        schemas = _motor_tools_schema_al(motor)
        assert schemas == []

    def test_araclar_schema_uretilir(self):
        from conversation_loop import _motor_tools_schema_al

        motor = MagicMock()
        motor._plugin_araclar = {
            "DOSYA_OKU": lambda p="": p,
            "WEB_ARA": lambda q="": q,
        }
        schemas = _motor_tools_schema_al(motor)
        assert len(schemas) == 2
        isimler = {s["function"]["name"] for s in schemas}
        assert "DOSYA_OKU" in isimler
        assert "WEB_ARA" in isimler

    def test_schema_format_gecerli(self):
        from conversation_loop import _motor_tools_schema_al

        motor = MagicMock()
        motor._plugin_araclar = {"TEST_ARAC": lambda: None}
        schemas = _motor_tools_schema_al(motor)
        s = schemas[0]
        assert s["type"] == "function"
        assert "name" in s["function"]
        assert "description" in s["function"]
        assert "parameters" in s["function"]
        assert s["function"]["parameters"]["type"] == "object"

    def test_maks_arac_siniri(self):
        from conversation_loop import _motor_tools_schema_al

        motor = MagicMock()
        motor._plugin_araclar = {f"ARAC_{i}": lambda: None for i in range(100)}
        schemas = _motor_tools_schema_al(motor, maks_arac=10)
        assert len(schemas) == 10

    def test_motor_plugin_araclar_yok(self):
        from conversation_loop import _motor_tools_schema_al

        motor = object()  # _plugin_araclar yok
        schemas = _motor_tools_schema_al(motor)
        assert schemas == []

    def test_hata_durumunda_bos_liste(self, monkeypatch):
        from conversation_loop import _motor_tools_schema_al

        motor = MagicMock()
        # _plugin_araclar property'si exception fırlatsın
        type(motor)._plugin_araclar = property(
            lambda self: (_ for _ in ()).throw(RuntimeError("hata"))
        )
        schemas = _motor_tools_schema_al(motor)
        assert schemas == []


# ── _interruptible_api_call uret_v2 önceliği ────────────────────────────────


class TestInterruptibleApiCallV2:
    def test_uret_v2_cagrilir_oncelikli(self):
        """Beyin'de uret_v2 varsa ve motor tools üretebiliyorsa uret_v2 çağrılır."""
        from conversation_loop import ConversationLoop

        beklenen = {"role": "assistant", "content": "v2 yanit", "tool_calls": []}
        mock_beyin = MagicMock()
        mock_beyin.uret_v2 = MagicMock(return_value=beklenen)
        mock_beyin.uret = MagicMock(return_value="v1 yanit")

        mock_motor = MagicMock()
        mock_motor._plugin_araclar = {"ARAC_1": lambda: None}

        loop = ConversationLoop(motor=mock_motor, beyin=mock_beyin)
        mesajlar = [
            {"role": "system", "content": SISTEM},
            {"role": "user", "content": "test"},
        ]
        sonuc = loop._interruptible_api_call(mesajlar, "chat_completions")
        assert sonuc is not None
        mock_beyin.uret_v2.assert_called_once()
        mock_beyin.uret.assert_not_called()

    def test_uret_v1_fallback_tools_yok(self):
        """Motor tools üretemiyorsa uret() kullanılır."""
        from conversation_loop import ConversationLoop

        mock_beyin = MagicMock()
        mock_beyin.uret_v2 = MagicMock()
        mock_beyin.uret = MagicMock(return_value="v1 yanit")

        mock_motor = MagicMock()
        mock_motor._plugin_araclar = {}  # boş → schema üretilemez

        loop = ConversationLoop(motor=mock_motor, beyin=mock_beyin)
        mesajlar = [{"role": "user", "content": "test"}]
        sonuc = loop._interruptible_api_call(mesajlar, "chat_completions")
        assert sonuc is not None
        mock_beyin.uret_v2.assert_not_called()
        mock_beyin.uret.assert_called_once()

    def test_uret_v2_yok_v1_kullanilir(self):
        """Beyin'de uret_v2 yoksa uret() çağrılır."""
        from conversation_loop import ConversationLoop

        mock_beyin = MagicMock(spec=["uret"])  # uret_v2 yok
        mock_beyin.uret = MagicMock(return_value="v1 yanit")

        mock_motor = MagicMock()
        mock_motor._plugin_araclar = {"ARAC": lambda: None}

        loop = ConversationLoop(motor=mock_motor, beyin=mock_beyin)
        mesajlar = [{"role": "user", "content": "test"}]
        sonuc = loop._interruptible_api_call(mesajlar, "chat_completions")
        assert sonuc is not None
        mock_beyin.uret.assert_called_once()
