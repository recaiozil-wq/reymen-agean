# -*- coding: utf-8 -*-
"""acp_adapter/client.py — ACP Istemci.

Diger ajanlara (Claude Code, ReYMeN, Codex) JSON-RPC istegi
gondermek icin kullanilir.
"""

import json
import logging
import socket
import subprocess
import sys
from typing import Any, Optional

logger = logging.getLogger("acp.client")


class ACPClient:
    """ACP istemci. Diger ajanlara istek gonderir."""

    def __init__(self):
        self._req_id = 0

    def _yeni_id(self) -> int:
        self._req_id += 1
        return self._req_id

    def _tcp_cagir(self, host: str, port: int, istek: dict) -> dict:
        """TCP ile ajan cagir."""
        try:
            with socket.create_connection((host, port), timeout=10) as sock:
                sock.sendall(json.dumps(istek).encode("utf-8"))
                data = sock.recv(65536)
                return json.loads(data.decode("utf-8"))
        except socket.timeout:
            return {"error": {"message": "Zaman asimi"}}
        except ConnectionRefusedError:
            return {"error": {"message": f"Baglanti reddedildi ({host}:{port})"}}
        except Exception as e:
            return {"error": {"message": str(e)}}

    def _stdio_cagir(self, komut: list[str], istek: dict) -> dict:
        """Stdio uzerinden ajan cagir (ornek: Claude Code)."""
        try:
            r = subprocess.run(
                komut,
                input=json.dumps(istek),
                capture_output=True, text=True, timeout=30,
            )
            if r.returncode == 0 and r.stdout.strip():
                return json.loads(r.stdout.strip())
            return {"error": {"message": f"Process error: {r.stderr[:200]}"}}
        except subprocess.TimeoutExpired:
            return {"error": {"message": "Zaman asimi"}}
        except Exception as e:
            return {"error": {"message": str(e)}}

    def cagir(self, method: str, params: dict = None, **baglanti) -> dict:
        """Bir ajanda method cagir.

        Args:
            method: Cagrilacak method adi
            params: Method parametreleri
            baglanti: Baglanti bilgileri
                - host, port: TCP baglantisi icin
                - komut: Stdio baglantisi icin (ornek: ["claude", "acp"])

        Returns:
            JSON-RPC yaniti
        """
        istek = {
            "jsonrpc": "2.0",
            "id": self._yeni_id(),
            "method": method,
            "params": params or {},
        }

        host = baglanti.get("host", "127.0.0.1")
        port = baglanti.get("port", 9100)
        komut = baglanti.get("komut")

        if komut:
            return self._stdio_cagir(komut, istek)
        return self._tcp_cagir(host, port, istek)

    def ping(self, **baglanti) -> bool:
        """Ajana ping at."""
        sonuc = self.cagir("ping", **baglanti)
        return "result" in sonuc

    def tool_listele(self, **baglanti) -> list:
        """Ajanin kullanabilecegi araclari listele."""
        sonuc = self.cagir("tools/list", **baglanti)
        return sonuc.get("result", {}).get("tools", [])

    def tool_cagir(self, tool_ad: str, args: dict = None, **baglanti) -> str:
        """Ajanda bir arac cagir."""
        sonuc = self.cagir("tools/call", {
            "name": tool_ad,
            "arguments": args or {},
        }, **baglanti)
        icerik = sonuc.get("result", {}).get("content", "")
        if isinstance(icerik, list):
            return " ".join(c.get("text", "") for c in icerik if c.get("type") == "text")
        return str(icerik)


if __name__ == "__main__":
    client = ACPClient()
    # Yerel ACP sunucusuna ping
    sonuc = client.ping(host="127.0.0.1", port=9100)
    print(f"ACP ping: {sonuc}")
    if sonuc:
        print(f"Tool'lar: {client.tool_listele(host='127.0.0.1', port=9100)}")
