# -*- coding: utf-8 -*-
"""gateway/webhook.py ve gateway/platforms/webhook.py testleri."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


# ── gateway/webhook.py testleri ──


class TestWebhookGateway:
    def test_inbound_sunucu_olustur(self):
        from gateway.webhook import WebhookGateway
        gw = WebhookGateway(port=18766)
        assert gw.port == 18766

    def test_baslat_durdur(self):
        from gateway.webhook import WebhookGateway
        gw = WebhookGateway(port=18888)
        port = gw.baslat()
        assert port == 18888
        gw.durdur()

    def test_outbound_gonder(self):
        from gateway.webhook import WebhookGateway
        gw = WebhookGateway()
        with patch("urllib.request.urlopen") as mock_urlopen:
            sonuc = gw.gonder("http://localhost:9999/test", "test mesaj")
            assert "Gönderildi" in sonuc or "Gonderildi" in sonuc
            mock_urlopen.assert_called_once()

    def test_outbound_hata(self):
        from gateway.webhook import WebhookGateway
        gw = WebhookGateway()
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = Exception("baglanti hatasi")
            sonuc = gw.gonder("http://localhost:9999/test", "test mesaj")
            assert "Hata" in sonuc or "hata" in sonuc

    def test_mesaj_isleyici_kaydet(self):
        from gateway.webhook import WebhookGateway, _WebhookHandler
        gw = WebhookGateway()
        fn = lambda m, p, v: None
        gw.mesaj_isleyici_kaydet(fn)
        assert _WebhookHandler.mesaj_isleyici is fn


# ── gateway/platforms/webhook.py testleri ──


class TestWebhookPlatform:
    def test_platform_adapter_olustur(self):
        from gateway.platforms.webhook import WebhookAdapter
        adapter = WebhookAdapter()
        assert adapter.platform == "webhook"

    def test_platform_adapter_mesaj_isleme(self):
        from gateway.platforms.webhook import WebhookAdapter
        adapter = WebhookAdapter()
        fn = lambda m, p, v: None
        adapter.mesaj_isleyici_kaydet(fn)
        assert adapter._mesaj_isleyici is fn

    def test_mesaj_gonder_basit(self):
        from gateway.platforms.webhook import mesaj_gonder
        with patch("requests.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            sonuc = mesaj_gonder("http://test.com/hook", "test mesaj")
            assert "Gonderildi" in sonuc or "Gönderildi" in sonuc

    def test_mesaj_gonder_gecersiz_url(self):
        from gateway.platforms.webhook import mesaj_gonder
        sonuc = mesaj_gonder("gecersiz-url", "test")
        assert "URL" in sonuc or "url" in sonuc

    def test_adapter_send_message(self):
        from gateway.platforms.webhook import WebhookAdapter
        adapter = WebhookAdapter()
        import asyncio
        sonuc = asyncio.run(adapter.send_message("http://localhost:9999/test", "test"))
        assert isinstance(sonuc, dict)


# ── gateway/platforms/signal.py testleri ──


class TestSignalPlatform:
    def test_signal_modul_import(self):
        import gateway.platforms.signal as signal_modul
        assert hasattr(signal_modul, "mesaj_gonder")

    def test_signal_mesaj_gonder(self):
        from gateway.platforms.signal import mesaj_gonder
        sonuc = mesaj_gonder("test", {"phone": "+905"})
        assert sonuc is not None

    def test_signal_fonksiyon_sayisi(self):
        import gateway.platforms.signal as signal_modul
        fonk_sayisi = sum(
            1 for name in dir(signal_modul)
            if callable(getattr(signal_modul, name)) and not name.startswith("_")
        )
        assert fonk_sayisi >= 5

    def test_signal_import_basarili(self):
        import gateway.platforms.signal
        assert True
