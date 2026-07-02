# -*- coding: utf-8 -*-
"""Kalite/Analytics dashboard testleri."""

import pytest
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


class TestKaliteDashboard:
    """Kalite dashboard template ve API testleri."""

    def test_quality_template_var(self):
        """quality.html template'i var mi?"""
        template_path = os.path.join(ROOT, "reymen/web_ui/templates/quality.html")
        assert os.path.exists(template_path), "quality.html bulunamadi"
        size = os.path.getsize(template_path)
        assert size > 2000, f"quality.html cok kucuk: {size} bytes"

    def test_kalite_api_routes_var(self):
        """Kalite API route'lari tanimli mi?"""
        from reymen.web_ui import app
        kalite_routes = [r.path for r in app.routes if "kalite" in r.path.lower()]
        assert len(kalite_routes) >= 7, f"Sadece {len(kalite_routes)} kalite route bulundu"
        required = ["/api/kalite/metrikler", "/api/kalite/coverage", "/api/kalite/hatalar"]
        for r in required:
            assert r in kalite_routes, f"{r} route eksik"

    def test_kalite_api_metrikler(self):
        """api_kalite_metrikler calisiyor mu?"""
        from reymen.web_ui import app
        from httpx import AsyncClient, ASGITransport
        import asyncio
        
        async def test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/api/kalite/metrikler")
                assert resp.status_code == 200
                assert "Test Coverage" in resp.text
        
        asyncio.run(test())

    def test_kalite_sayfasi(self):
        """Kalite sayfasi yukleniyor mu?"""
        from reymen.web_ui import app
        from httpx import AsyncClient, ASGITransport
        import asyncio
        
        async def test():
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                resp = await client.get("/kalite")
                assert resp.status_code == 200
                assert "Kalite" in resp.text or "kalite" in resp.text.lower()
        
        asyncio.run(test())

    def test_dashboard_cli(self):
        """CLI dashboard komutu calisiyor mu?"""
        from reymen.reymen_cli.subcommands.dashboard import build_dashboard_parser, run_dashboard
        parser = build_dashboard_parser()
        assert parser is not None
        # --durum ile calis
        args = parser.parse_args(["--durum"])
        # Hata vermemeli
        run_dashboard(args)
