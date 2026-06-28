# -*- coding: utf-8 -*-
"""ReYMeN_tools_mcp_server.py — ReYMeN MCP tool sunucu transportu.

MCP protokolu ile ReYMeN tool'larini disa aktarir.
Tool'lari MCP server olarak yayinlar ve cagri alir.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

from agent.transports.base import Transport, TransportHatasi

logger = logging.getLogger(__name__)

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.responses import JSONResponse
except ImportError:
    uvicorn = None
    FastAPI = None
    HTTPException = None
    Request = None
    JSONResponse = None
    logger.warning(
        "fastapi/uvicorn yuklenemedi — ReYMeNToolsMCPServer devre disi."
    )


class ReYMeNToolsMCPServerTransport(Transport):
    """ReYMeN MCP tool sunucu transportu.

    MCP (Model Context Protocol) protokolu ile ReYMeN tool'larini
    HTTP server olarak yayinlar. Tool listeleme ve cagirma
    islemlerini JSON-RPC 2.0 uzerinden saglar.

    Parametreler:
        host: Sunucu adresi (varsayilan: 0.0.0.0).
        port: Sunucu portu (varsayilan: 9000).
        tools: Disa aktarilacak tool tanimlari listesi.
        api_key: Opsiyonel API anahtari (Authorization Bearer).
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9000,
        tools: Optional[List[Dict[str, Any]]] = None,
        api_key: str = "",
    ):
        self.host = host
        self.port = port
        self.tools = tools or []
        self.api_key = api_key
        self._app: Optional["FastAPI"] = None
        self._msg_id = 0

        if FastAPI is not None:
            self._app_olustur()

    # ── Transport Arayuzu ───────────────────────────────────────────

    def send(self, mesajlar: list, **kwargs) -> str:
        """MCP tool cagrisini isler ve sonucu dondurur.

        Args:
            mesajlar: MCP istekleri [{"name": "...", "arguments": {...}}].
            **kwargs: Ek parametreler.

        Returns:
            Tool cagrisi sonucu.
        """
        if not mesajlar:
            return ""

        for istek in mesajlar:
            if isinstance(istek, dict) and "name" in istek:
                return self._tool_calistir(
                    istek["name"],
                    istek.get("arguments", {}),
                )

        return ""

    def ping(self) -> bool:
        """MCP sunucu erisilebilir mi?"""
        try:
            import requests
            r = requests.get(
                f"http://{self.host}:{self.port}/health",
                timeout=5,
            )
            return r.status_code == 200
        except Exception:
            return False

    def supports_streaming(self) -> bool:
        return False

    # ── Tool Yonetimi ───────────────────────────────────────────────

    def tool_ekle(self, tool_tanimi: Dict[str, Any]):
        """Bir tool tanimi ekler.

        Args:
            tool_tanimi: MCP formatinda tool tanimi.
                {"name": "...", "description": "...", "inputSchema": {...}}
        """
        self.tools.append(tool_tanimi)
        logger.info("Tool eklendi: %s", tool_tanimi.get("name"))

    def tool_sil(self, tool_adi: str) -> bool:
        """Bir tool tanimini siler.

        Args:
            tool_adi: Silinecek tool adi.

        Returns:
            True basarili, False bulunamadi.
        """
        onceki = len(self.tools)
        self.tools = [t for t in self.tools if t.get("name") != tool_adi]
        silindi = len(self.tools) < onceki
        if silindi:
            logger.info("Tool silindi: %s", tool_adi)
        return silindi

    def _tool_calistir(self, name: str, arguments: Dict[str, Any]) -> str:
        """Bir tool'u calistirir (alt sinif ezmeli)."""
        # Alt sinif tarafindan ezilmek icin tasarlanmis
        # Varsayilan: tool adi bir fonksiyon olarak cagrilir
        raise TransportHatasi(
            f"Tool '{name}' icin uygun isleyici tanimlanmamis. "
            "Alt sinifta _tool_calistir() metodunu ezin."
        )

    # ── FastAPI Uygulamasi ──────────────────────────────────────────

    def _app_olustur(self):
        """MCP sunucu FastAPI uygulamasini olusturur."""
        if FastAPI is None:
            return

        self._app = FastAPI(
            title="ReYMeN Tools MCP Server",
            description="ReYMeN tool'larini MCP protokolu ile disa aktarir",
            version="1.0.0",
        )

        @self._app.get("/health")
        async def saglik_kontrol():
            return {
                "status": "ok",
                "transport": "ReYMeN_tools_mcp",
                "tool_sayisi": len(self.tools),
            }

        @self._app.post("/mcp")
        async def mcp_handler(request: Request):
            """MCP JSON-RPC 2.0 isteklerini isler."""
            if self.api_key:
                auth = request.headers.get("Authorization", "")
                if auth != f"Bearer {self.api_key}":
                    if HTTPException is not None:
                        raise HTTPException(status_code=401, detail="Yetkisiz")

            try:
                body = await request.json()
            except Exception:
                return JSONResponse(
                    status_code=400,
                    content={
                        "jsonrpc": "2.0",
                        "error": {"code": -32700, "message": "Gecersiz JSON"},
                        "id": None,
                    },
                )

            method = body.get("method", "")
            params = body.get("params", {})
            req_id = body.get("id", None)

            try:
                if method == "tools/list":
                    sonuc = self._tools_listele(params)
                elif method == "tools/call":
                    sonuc = self._tools_call(params)
                elif method == "ping":
                    sonuc = {}
                else:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "jsonrpc": "2.0",
                            "error": {
                                "code": -32601,
                                "message": f"Metod bulunamadi: {method}",
                            },
                            "id": req_id,
                        },
                    )

                return {
                    "jsonrpc": "2.0",
                    "result": sonuc,
                    "id": req_id,
                }
            except TransportHatasi as e:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32000, "message": str(e)},
                    "id": req_id,
                }
            except Exception as e:
                logger.exception("MCP isleme hatasi")
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32603, "message": str(e)},
                    "id": req_id,
                }

    def _tools_listele(self, params: dict) -> dict:
        """MCP tools/list metodunu isler."""
        return {"tools": self.tools}

    def _tools_call(self, params: dict) -> dict:
        """MCP tools/call metodunu isler."""
        name = params.get("name", "")
        arguments = params.get("arguments", {})

        if not name:
            raise TransportHatasi("Tool adi belirtilmemis.")

        # Tool'un tanimli oldugunu kontrol et
        tool_var = any(t.get("name") == name for t in self.tools)
        if not tool_var:
            raise TransportHatasi(f"Tool bulunamadi: {name}")

        try:
            sonuc = self._tool_calistir(name, arguments)
            return {
                "content": [
                    {"type": "text", "text": str(sonuc)},
                ],
            }
        except TransportHatasi:
            raise
        except Exception as e:
            raise TransportHatasi(
                f"Tool calistirilirken hata: {name} — {e}"
            ) from e

    # ── Sunucu Baslatma ─────────────────────────────────────────────

    def baslat(self):
        """MCP sunucusunu baslatir."""
        if uvicorn is None:
            raise TransportHatasi(
                "uvicorn yuklenemedi — sunucu baslatilamadi."
            )
        if self._app is None:
            raise TransportHatasi("FastAPI uygulamasi olusturulamadi.")

        logger.info(
            "ReYMeN MCP sunucu baslatiliyor: %s:%s", self.host, self.port
        )
        uvicorn.run(
            self._app,
            host=self.host,
            port=self.port,
            log_level="info",
        )

    @property
    def app(self) -> Optional["FastAPI"]:
        """FastAPI uygulamasina erisim."""
        return self._app


# ── Kolay Kurulum ──────────────────────────────────────────────────────

def transport_kur(
    host: str = "0.0.0.0",
    port: int = 9000,
    tools: Optional[List[Dict[str, Any]]] = None,
    api_key: str = "",
) -> ReYMeNToolsMCPServerTransport:
    """ReYMeNToolsMCPServerTransport ornegi olusturur."""
    return ReYMeNToolsMCPServerTransport(
        host=host, port=port, tools=tools, api_key=api_key,
    )
