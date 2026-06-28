# -*- coding: utf-8 -*-
"""tests/test_provider.py — Provider modulleri testleri."""

import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from chat_completion_helpers import ChatHelper
from auxiliary_client import AuxiliaryClient
from web_search_provider import WebSearchProvider


class TestChatHelper:
    def test_chat_helper_olusturma(self):
        """ChatHelper baslatma."""
        ch = ChatHelper(model_adi="test-model")
        assert ch is not None
        assert ch._model_adi == "test-model"

    def test_mesaj_hazirla(self):
        """Mesaj hazirlama."""
        ch = ChatHelper()
        mesaj = ch.mesaj_hazirla("sistem", "test mesaj")
        assert mesaj is not None
        if isinstance(mesaj, dict):
            assert mesaj.get("role") == "system" or mesaj.get("rol") == "sistem"
        elif isinstance(mesaj, list):
            assert len(mesaj) > 0

    def test_mesaj_hazirla_kullanici(self):
        """Kullanici mesaji hazirlama."""
        ch = ChatHelper()
        mesaj = ch.mesaj_hazirla("user", "Merhaba dunya")
        assert mesaj is not None

    def test_mesaj_hazirla_json(self):
        """JSON formatinda mesaj hazirlama."""
        ch = ChatHelper()
        mesaj = ch.mesaj_hazirla("assistant", json.dumps({"yanit": "test"}))
        assert mesaj is not None

    def test_token_say(self):
        """Token sayma."""
        ch = ChatHelper()
        token = ch.token_say("Bu bir test mesajidir")
        assert isinstance(token, int)
        assert token > 0

    def test_token_say_bos(self):
        """Bos metin token sayma."""
        ch = ChatHelper()
        token = ch.token_say("")
        assert isinstance(token, int)

    def test_token_say_uzun(self):
        """Uzun metin token sayma."""
        ch = ChatHelper()
        token = ch.token_say("kelime " * 100)
        assert token > 10

    def test_istatistik(self):
        """Istatistik takibi."""
        ch = ChatHelper()
        ch.mesaj_hazirla("user", "test")
        istatistik = ch._istatistik
        assert "toplam_mesaj" in istatistik
        assert "toplam_token" in istatistik

    def test_model_adi_kontrol(self):
        """Model adi dogrulama."""
        ch = ChatHelper(model_adi="gpt-4")
        ch2 = ChatHelper()
        assert ch._model_adi == "gpt-4"
        assert ch2._model_adi == "varsayilan"


class TestAuxiliaryClient:
    def test_auxiliary_client_olusturma(self):
        """AuxiliaryClient baslatma."""
        ac = AuxiliaryClient()
        assert ac is not None

    def test_get_method(self):
        """GET metodu varligi."""
        ac = AuxiliaryClient()
        assert hasattr(ac, "get") or hasattr(ac, "al")

    def test_post_method(self):
        """POST metodu varligi."""
        ac = AuxiliaryClient()
        assert hasattr(ac, "post") or hasattr(ac, "gonder")


class TestWebSearchProvider:
    def test_web_search_olusturma(self):
        """WebSearchProvider baslatma."""
        wsp = WebSearchProvider()
        assert wsp is not None

    def test_ara_method(self):
        """ara() metodu varligi."""
        wsp = WebSearchProvider()
        assert hasattr(wsp, "ara") or hasattr(wsp, "search")
