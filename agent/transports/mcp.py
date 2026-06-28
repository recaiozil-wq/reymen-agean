# -*- coding: utf-8 -*-
"""mcp.py — MCP transportu.

Alt-ajanlar icin MCP istemci.
MCP stdio transport ile baglanti kurar.
mcp_serve.py'deki mevcut sunucuyla uyumlu.
"""

import json
import logging
import subprocess
import threading
from typing import Any, Iterator, Optional

from agent.transports.base import Transport, TransportHatasi

logger = logging.getLogger(__name__)


class MCPTransport(Transport):
    """MCP (Model Context Protocol) transportu.

    Alt-ajanlari MCP sunucusu uzerinden calistirir.
    Stdio transport ile baglanti kurar.

    Parametreler:
        server_command: MCP sunucu komutu (ornek: ["python", "mcp_serve.py"]).
        tools: Kullanilacak MCP araclari listesi.
    """

    def __init__(
        self,
        server_command: list = None,
        tools: list = None,
        calisma_dizini: str = None,
    ):
        self.server_command = server_command or ["python", "mcp_serve.py"]
        self.tools = tools or []
        self.calisma_dizini = calisma_dizini
        self._surec: Optional[subprocess.Popen] = None
        self._kilit = threading.Lock()
        self._msg_id = 0

    # ── Transport Arayuzu ───────────────────────────────────────────

    def send(self, mesajlar: list, **kwargs) -> str:
        """Mesaji MCP sunucusuna gonderir.

        tools/call metodu ile belirtilen araci calistirir.

        Args:
            mesajlar: Islem parametreleri [{"name": "...", "arguments": {...}}].
            **kwargs: Ek parametreler.

        Returns:
            MCP sunucusundan gelen yanit metni.
        """
        if not self._surec:
            self._baglan()

        if not mesajlar:
            return ""

        for islem in mesajlar:
            if isinstance(islem, dict) and "name" in islem:
                sonuc = self._tool_cagir(
                    islem["name"],
                    islem.get("arguments", {}),
                )
                return sonuc

        return ""

    def ping(self) -> bool:
        """MCP sunucusu canli mi?"""
        try:
            yanit = self._jsonrpc_gonder("ping", {})
            return yanit is not None
        except Exception:
            return False

    def supports_streaming(self) -> bool:
        return False

    # ── Baglanti Yonetimi ───────────────────────────────────────────

    def _baglan(self):
        """MCP sunucusuna stdio uzerinden baglan."""
        if self._surec:
            return

        try:
            self._surec = subprocess.Popen(
                self.server_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.calisma_dizini,
            )
            # initialize
            yanit = self._jsonrpc_gonder("initialize", {
                "protocolVersion": "2024-11-05",
                "clientInfo": {"name": "ReYMeN-transport", "version": "1.0.0"},
                "capabilities": {},
            })
            if yanit:
                logger.info("MCP baglantisi basarili: %s", yanit.get("serverInfo", {}))
            else:
                raise TransportHatasi("MCP initialize basarisiz")
        except Exception as e:
            self._surec = None
            raise TransportHatasi(f"MCP baglanti hatasi: {e}") from e

    def _koprul(self):
        """MCP baglantisini kapat."""
        with self._kilit:
            if self._surec:
                try:
                    self._surec.terminate()
                    self._surec.wait(timeout=5)
                except Exception:
                    self._surec.kill()
                self._surec = None

    def __del__(self):
        self._koprul()

    # ── JSON-RPC Iletisimi ───────────────────────────────────────────

    def _sonraki_id(self) -> int:
        with self._kilit:
            self._msg_id += 1
            return self._msg_id

    def _jsonrpc_gonder(self, method: str, params: dict) -> Optional[dict]:
        """JSON-RPC 2.0 istegi gonderir ve yaniti bekler."""
        if not self._surec:
            return None

        istek = {
            "jsonrpc": "2.0",
            "id": self._sonraki_id(),
            "method": method,
            "params": params,
        }

        with self._kilit:
            try:
                satir = json.dumps(istek, ensure_ascii=False)
                self._surec.stdin.write(satir + "\n")
                self._surec.stdin.flush()

                yanit_satir = self._surec.stdout.readline()
                if not yanit_satir:
                    return None
                yanit = json.loads(yanit_satir.strip())
                if "error" in yanit:
                    raise TransportHatasi(
                        f"MCP hatasi ({yanit['error'].get('code')}): "
                        f"{yanit['error'].get('message')}"
                    )
                return yanit.get("result")
            except Exception as e:
                logger.error("JSON-RPC iletisim hatasi: %s", e)
                return None

    def _tool_cagir(self, name: str, arguments: dict) -> str:
        """MCP aracini cagirir."""
        sonuc = self._jsonrpc_gonder("tools/call", {
            "name": name,
            "arguments": arguments,
        })
        if not sonuc:
            return "MCP arac yanit vermedi."
        icerik = sonuc.get("content", [])
        metinler = [
            p.get("text", "") for p in icerik if p.get("type") == "text"
        ]
        return "\n".join(metinler)

    def tool_listele(self) -> list:
        """MCP sunucusundaki kullanilabilir araclari listeler."""
        sonuc = self._jsonrpc_gonder("tools/list", {})
        return (sonuc or {}).get("tools", [])


# ── Kolay Kurulum ──────────────────────────────────────────────────────

def transport_kur(server_command: list = None, tools: list = None,
                  calisma_dizini: str = None) -> MCPTransport:
    """MCPTransport ornegi olusturur."""
    return MCPTransport(
        server_command=server_command,
        tools=tools,
        calisma_dizini=calisma_dizini,
    )
