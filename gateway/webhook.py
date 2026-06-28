# -*- coding: utf-8 -*-
"""gateway/webhook.py — Webhook Platform.

Gelen HTTP webhook'larını ReYMeN'e yönlendirir.
urllib ile bağımlılıksız HTTP sunucu.
"""

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Optional
import logging
logger = logging.getLogger(__name__)

WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", "8766"))
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")


class _WebhookHandler(BaseHTTPRequestHandler):
    mesaj_isleyici: Optional[Callable] = None

    def do_POST(self):
        try:
            uzunluk = int(self.headers.get("Content-Length", 0))
            govde = self.rfile.read(uzunluk).decode("utf-8")

            # Secret doğrula
            if WEBHOOK_SECRET:
                gelen_imza = self.headers.get("X-Webhook-Secret", "")
                if gelen_imza != WEBHOOK_SECRET:
                    self._yanit(403, {"error": "Yetkisiz"})
                    return

            veri = json.loads(govde) if govde else {}
            mesaj = veri.get("text") or veri.get("message") or json.dumps(veri)[:200]

            if self.mesaj_isleyici:
                threading.Thread(
                    target=self.mesaj_isleyici,
                    args=(mesaj, "webhook", veri),
                    daemon=True,
                ).start()

            self._yanit(200, {"status": "ok"})
        except Exception as e:
            self._yanit(500, {"error": str(e)})

    def do_GET(self):
        if self.path == "/health":
            self._yanit(200, {"status": "up", "platform": "webhook"})
        else:
            self._yanit(404, {"error": "Bulunamadı"})

    def _yanit(self, kod: int, veri: dict):
        govde = json.dumps(veri).encode("utf-8")
        self.send_response(kod)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(govde)))
        self.end_headers()
        self.wfile.write(govde)

    def log_message(self, *args):
        pass


class WebhookGateway:
    def __init__(self, port: int = WEBHOOK_PORT):
        self.port = port
        self._sunucu: Optional[HTTPServer] = None
        self._isleyici: Optional[Callable] = None

    def mesaj_isleyici_kaydet(self, fn: Callable):
        self._isleyici = fn
        _WebhookHandler.mesaj_isleyici = fn

    def baslat(self):
        _WebhookHandler.mesaj_isleyici = self._isleyici
        self._sunucu = HTTPServer(("0.0.0.0", self.port), _WebhookHandler)
        t = threading.Thread(target=self._sunucu.serve_forever, daemon=True)
        t.start()
        return self.port

    def durdur(self):
        if self._sunucu:
            self._sunucu.shutdown()

    def gonder(self, hedef_url: str, mesaj: str) -> str:
        """Dışa webhook gönder."""
        import urllib.request
        govde = json.dumps({"text": mesaj}).encode("utf-8")
        try:
            req = urllib.request.Request(
                hedef_url, data=govde,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=10)
            return "[Webhook]: Gönderildi."
        except Exception as e:
            return f"[Webhook]: Hata — {e}"


if __name__ == "__main__":
    gw = WebhookGateway(port=8766)
    gw.mesaj_isleyici_kaydet(lambda m, p, v: print(f"[{p}] {m}"))
    p = gw.baslat()
    print(f"Webhook dinleniyor: http://localhost:{p}")
    import time; time.sleep(2)
    gw.durdur()
