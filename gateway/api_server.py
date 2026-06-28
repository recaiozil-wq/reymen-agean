# -*- coding: utf-8 -*-
"""gateway/api_server.py — REST API Platformu.

HTTP uzerinden gelen istekleri kabul eder (FastAPI tabanli).
"""

import os
import threading
import json
from typing import Optional

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


_son_mesaj = ""
_son_mesaj_kilit = threading.Lock()
app = None


def _app_olustur():
    global app
    if app is not None:
        return app

    app = FastAPI(title="ReYMeN API", version="1.0.0")

    @app.get("/")
    async def kok():
        return {"service": "ReYMeN API", "status": "running"}

    @app.get("/health")
    async def saglik():
        return {"status": "ok"}

    @app.post("/mesaj")
    async def mesaj_al(request: Request):
        data = await request.json()
        with _son_mesaj_kilit:
            global _son_mesaj
            _son_mesaj = data.get("text", "")
        return {"status": "received"}

    @app.get("/son-mesaj")
    async def son_mesaj_getir():
        with _son_mesaj_kilit:
            return {"text": _son_mesaj}

    return app


def baslat(port: int = 8999):
    if not FASTAPI_AVAILABLE:
        return
    t = threading.Thread(
        target=lambda: uvicorn.run(
            _app_olustur(),
            host="127.0.0.1",
            port=port,
            log_level="error",
        ),
        daemon=True,
    )
    t.start()


def durdur():
    pass


def mesaj_gonder(hedef: str, mesaj: str) -> str:
    """API uzerinden mesaj gonder (istemci tarafi)."""
    try:
        import requests
        r = requests.post(
            f"{hedef}/mesaj",
            json={"text": mesaj, "source": "ReYMeN"},
            timeout=5,
        )
        if r.status_code == 200:
            return "[API]: Mesaj gonderildi."
        return f"[API]: Hata {r.status_code}"
    except Exception as e:
        return f"[API]: Hata: {e}"
