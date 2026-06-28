# -*- coding: utf-8 -*-
"""tests/test_gateway.py — Gateway platform testleri."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestGatewayPlatforms:
    def test_platform_listesi(self):
        from gateway.platforms import platform_listele
        platforms = platform_listele()
        assert len(platforms) >= 10

    def test_platform_webhook(self):
        from gateway.platforms import mesaj_gonder
        sonuc = mesaj_gonder("webhook", "https://example.com", "test")
        assert "Webhook" in sonuc


class TestGatewaySession:
    def test_session_olusturma(self):
        from gateway.session import SessionManager
        sm = SessionManager()
        oturum = sm.olustur("test", "kullanici1")
        assert oturum.id is not None
        assert len(sm.liste()) >= 1


class TestGatewayMirror:
    def test_mirror_ekle(self):
        from gateway.mirror import aynalayici
        aynalayici.ekle("telegram", ["discord", "slack"])
        assert len(aynalayici.kurallar()) >= 1


class TestGatewayPairing:
    def test_pairing_kod(self):
        from gateway.pairing import eslestirici
        sonuc = eslestirici.eslestir("test-cihaz", "telegram")
        assert "kod" in sonuc
        assert "token" in sonuc
