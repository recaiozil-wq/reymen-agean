# -*- coding: utf-8 -*-
"""gateway/platforms/api_server.py — Gateway API Sunucusu.

Diger platformlarin HTTP endpoint'lerini yonetir.
Flask veya FastAPI tabanli. Opsiyonel bagimlilik.
"""

import os
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

# Opsiyonel bagimliliklar
_FRAMEWORK = None  # "flask" veya "fastapi" olarak ayarlanir

try:
    from flask import Flask, request, jsonify
    _FRAMEWORK = "flask"
except ImportError:
    Flask = None
    jsonify = None

if _FRAMEWORK is None:
    try:
        from fastapi import FastAPI, Request
        from pydantic import BaseModel
        _FRAMEWORK = "fastapi"
    except ImportError:
        FastAPI = None

_app = None
_server_instance = None


def _get_app():
    """Flask veya FastAPI uygulamasi olusturur."""
    global _app
    if _app is not None:
        return _app

    if _FRAMEWORK == "flask":
        _app = Flask("gateway_api")

        @_app.route("/health", methods=["GET"])
        def health():
            return jsonify({"durum": "saglikli", "platform": "gateway-api"})

        @_app.route("/send", methods=["POST"])
        def api_send():
            data = request.get_json(force=True, silent=True) or {}
            platform_adi = data.get("platform", "")
            hedef = data.get("hedef", "")
            mesaj = data.get("mesaj", "")

            if not all([platform_adi, hedef, mesaj]):
                return jsonify({"durum": "hata", "hata": "Eksik parametreler: platform, hedef, mesaj"}), 400

            try:
                mod = __import__(f"gateway.platforms.{platform_adi}", fromlist=["send_message"])
                sonuc = mod.send_message(hedef, mesaj, **data.get("kwargs", {}))
                return jsonify(sonuc)
            except ImportError:
                return jsonify({"durum": "hata", "hata": f"Platform bulunamadi: {platform_adi}"}), 404
            except Exception as e:
                return jsonify({"durum": "hata", "hata": str(e)}), 500

        @_app.route("/platforms", methods=["GET"])
        def api_platforms():
            return jsonify({"platform": "gateway-api"})

    elif _FRAMEWORK == "fastapi":
        from fastapi import FastAPI, Request

        _app = FastAPI(title="Gateway API", version="1.0.0")

        @_app.get("/health")
        async def health():
            return {"durum": "saglikli", "platform": "gateway-api"}

        @_app.post("/send")
        async def api_send(request: Request):
            data = await request.json()
            platform_adi = data.get("platform", "")
            hedef = data.get("hedef", "")
            mesaj = data.get("mesaj", "")

            if not all([platform_adi, hedef, mesaj]):
                return {"durum": "hata", "hata": "Eksik parametreler: platform, hedef, mesaj"}

            try:
                import importlib
                mod = importlib.import_module(f"gateway.platforms.{platform_adi}")
                sonuc = mod.send_message(hedef, mesaj, **data.get("kwargs", {}))
                return sonuc
            except ImportError:
                return {"durum": "hata", "hata": f"Platform bulunamadi: {platform_adi}"}
            except Exception as e:
                return {"durum": "hata", "hata": str(e)}

        @_app.get("/platforms")
        async def api_platforms():
            return {"platform": "gateway-api", "framework": "fastapi"}

    else:
        _app = None

    return _app


def send_message(hedef: str, mesaj: str, **kwargs) -> dict:
    """Gateway API sunucusu uzerinden mesaj gonderir.

    Bu fonksiyon dogrudan bir mesaj gondermekten ziyade,
    API sunucusunun bir endpoint'ini cagirarak mesaj gonderir.

    Args:
        hedef: Hedef URL (ornegin: http://localhost:5000/send)
        mesaj: Gonderilecek mesaj icerigi

    Keyword Args:
        platform: Platform adi (ornegin: "slack", "discord")
        kwargs: Platforma ozel ek parametreler

    Returns:
        dict: {"durum": "basarili", ...} veya {"durum": "hata", ...}
    """
    try:
        import requests
        platform_adi = kwargs.get("platform", "webhook")
        payload = {
            "platform": platform_adi,
            "hedef": hedef,
            "mesaj": mesaj,
            "kwargs": {k: v for k, v in kwargs.items() if k != "platform"},
        }
        r = requests.post(hedef, json=payload, timeout=10)
        return r.json() if r.headers.get("content-type", "").startswith("application/json") else {"durum": str(r.status_code)}
    except ImportError:
        return {"durum": "hata", "hata": "requests kutuphanesi yok."}
    except Exception as e:
        return {"durum": "hata", "hata": str(e)}


class APIServerAdapter:
    """API Sunucu Adaptoru — upstream Hermes uyumluluk katmani.

    Gateway API sunucusu icin adapter sinifi.
    Her platform adapteri gibi send_message, ping metodlarini uygular.
    """

    def __init__(self, config: Any = None):
        self._config = config

    def send_message(self, hedef: str, mesaj: str, **kwargs) -> dict:
        """Mesaj gonder (API uzerinden)."""
        return send_message(hedef, mesaj, **kwargs)

    def ping(self) -> bool:
        """Saglik kontrolu."""
        return ping()


def ping() -> bool:
    """API sunucusunun calisip calismadigini kontrol eder.

    Framework (Flask/FastAPI) kurulu mu kontrol eder.

    Returns:
        bool: Framework kurulu ise True
    """
    return _FRAMEWORK is not None
