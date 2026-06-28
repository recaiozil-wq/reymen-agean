# -*- coding: utf-8 -*-
"""acp_adapter/server.py — ACP Sunucu.

JSON-RPC 2.0 uzerinden diger ajanlarin ReYMeN'e
istek gondermesini saglar. stdio veya TCP uzerinden calisir.
"""

import json
import logging
import socket
import sys
import threading
from typing import Any, Callable

logger = logging.getLogger("acp.server")

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "ReYMeN", "version": "1.0.0"}
ReYMeN_VERSION = SERVER_INFO["version"]


class ACPServer:
    """ACP sunucu. Ajanlarin ReYMeN'e istek gondermesini saglar."""

    def __init__(self, host: str = "127.0.0.1", port: int = 9100):
        self.host = host
        self.port = port
        self._running = False
        self._tools: dict[str, Callable] = {}
        self._server_socket = None
        self._thread = None

    def tool_kaydet(self, ad: str, fonksiyon: Callable):
        """Bir aracı ACP'ye kaydet.

        Args:
            ad: Arac adi (ornek: "run", "status")
            fonksiyon: Cagrilacak fonksiyon (parametre=dict -> str)
        """
        self._tools[ad] = fonksiyon

    def _yanit(self, req_id: Any, sonuc: Any) -> str:
        return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": sonuc})

    def _hata(self, req_id: Any, code: int, mesaj: str) -> str:
        return json.dumps({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": code, "message": mesaj},
        })

    def _istek_isle(self, istek: dict) -> str:
        method = istek.get("method", "")
        req_id = istek.get("id")
        params = istek.get("params", {})

        if method == "initialize":
            return self._yanit(req_id, {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": SERVER_INFO,
                "capabilities": {"tools": list(self._tools.keys())},
            })
        elif method == "tools/list":
            tools_list = [
                {"name": ad, "description": f"ACP tool: {ad}"}
                for ad in self._tools
            ]
            return self._yanit(req_id, {"tools": tools_list})
        elif method == "tools/call":
            name = params.get("name", "")
            args = params.get("arguments", {})
            fonk = self._tools.get(name)
            if not fonk:
                return self._hata(req_id, -32601, f"Tool not found: {name}")
            try:
                sonuc = fonk(args)
                return self._yanit(req_id, {"content": str(sonuc)})
            except Exception as e:
                return self._hata(req_id, -32603, str(e))
        elif method == "ping":
            return self._yanit(req_id, {})
        else:
            return self._hata(req_id, -32601, f"Method not found: {method}")

    def _tcp_dinle(self):
        """TCP socket uzerinden gelen istekleri dinle."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        self._server_socket.settimeout(1.0)

        logger.info(f"ACP sunucu {self.host}:{self.port}'de dinliyor")
        while self._running:
            try:
                conn, addr = self._server_socket.accept()
                t = threading.Thread(target=self._baglanti_isle, args=(conn, addr), daemon=True)
                t.start()
            except socket.timeout:
                continue
            except Exception as e:
                if self._running:
                    logger.error(f"Baglanti hatasi: {e}")

    def _baglanti_isle(self, conn: socket.socket, addr: tuple):
        """Tek bir TCP baglantisindaki istekleri isle."""
        with conn:
            conn.settimeout(30)
            try:
                data = conn.recv(65536)
                if data:
                    istek = json.loads(data.decode("utf-8"))
                    yanit = self._istek_isle(istek)
                    conn.sendall(yanit.encode("utf-8"))
            except Exception as e:
                logger.debug(f"Baglanti isleme hatasi ({addr}): {e}")

    def _stdio_dinle(self):
        """stdin uzerinden gelen istekleri isle."""
        for satir in sys.stdin:
            satir = satir.strip()
            if not satir:
                continue
            try:
                istek = json.loads(satir)
                yanit = self._istek_isle(istek)
                print(yanit, flush=True)
            except json.JSONDecodeError as e:
                print(self._hata(None, -32700, f"Parse error: {e}"), flush=True)
            except Exception as e:
                print(self._hata(None, -32603, str(e)), flush=True)

    def baslat(self, mod: str = "tcp"):
        """Sunucuyu baslat.

        Args:
            mod: "tcp" (TCP socket) veya "stdio" (stdin/stdout)
        """
        self._running = True
        if mod == "tcp":
            self._thread = threading.Thread(target=self._tcp_dinle, daemon=True)
            self._thread.start()
        elif mod == "stdio":
            self._stdio_dinle()

    def durdur(self):
        self._running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")


# ---------------------------------------------------------------------------
# ReYMeNACPAgent — ACP ajan sınıfı (entry.py tarafından import edilir)
# ---------------------------------------------------------------------------


class ReYMeNACPAgent:
    """ACP protokolü üzerinden çalışan ReYMeN ajanı.

    ``entry.py`` bu sınıfı ``acp.run_agent()`` ile çalıştırır.
    Gerçek ACP SDK'sı kurulduğunda, ``run_agent`` JSON-RPC 2.0
    transport döngüsünü başlatır ve bu ajanın metodlarını çağırır.
    """

    def __init__(self) -> None:
        self._initialized = False

    async def initialize(self) -> None:
        """Ajanı başlat."""
        logger.info("ReYMeNACPAgent başlatılıyor...")
        self._initialized = True

    async def close(self) -> None:
        """Ajanı kapat."""
        logger.info("ReYMeNACPAgent kapatılıyor.")
        self._initialized = False

    async def prompt(
        self,
        text: str,
        session_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Bir prompt işle.

        Args:
            text: Prompt metni.
            session_id: Oturum ID'si (opsiyonel).
            **kwargs: Ek parametreler.

        Returns:
            Yanıt verisi.
        """
        # Stub — gerçek SDK burada AIAgent'e yönlendirir.
        return {"content": f"Processed: {text[:60]}..."}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = ACPServer(port=9100)
    server.tool_kaydet("ping", lambda args: "pong")
    server.tool_kaydet("status", lambda args: json.dumps({"durum": "hazir", "versiyon": "1.0.0"}))
    print(f"ACP sunucu baslatiliyor (port {server.port})...")
    server.baslat("tcp")

    # Sonsuz bekle
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.durdur()
