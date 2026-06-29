# -*- coding: utf-8 -*-
"""
reymen/core/mcp_server.py — ReYMeN MCP Server Host (Hermes seviyesi).

ReYMeN'i bir MCP (Model Context Protocol) sunucusu olarak yayınlar.
Diğer MCP client'ları (Claude Code, Cursor, Windsurf vb.) buraya bağlanıp
ReYMeN'in tool'larını, resource'larını ve prompt'larını kullanabilir.

Desteklenen MCP özellikleri:
  - tools/list, tools/call
  - resources/list, resources/read
  - prompts/list, prompts/get
  - roots/list
  - Notifications (initialized, roots/list_changed)
  - Streamable HTTP (SSE)
  - Dynamic tool/resource/prompt registration
  - JSON Schema argument validation
  - Session management (multi-client)
  - Ping/health

Kullanım:
    # Stdio (Claude Code entegrasyonu)
    python -m reymen.core.mcp_server --transport stdio

    # HTTP
    python -m reymen.core.mcp_server --transport http --port 9000

Claude Code (.claude/settings.json):
    "mcpServers": {
      "ReYMeN": {
        "command": "python",
        "args": ["-m", "reymen.core.mcp_server", "--transport", "stdio"]
      }
    }
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

logger = logging.getLogger(__name__)

# ── Sabitler ────────────────────────────────────────────────────────────

PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "ReYMeN", "version": "2.0.0"}

# ── JSON Schema doğrulama ───────────────────────────────────────────────

def _schema_dogrula(schema: dict, data: dict) -> str | None:
    """JSON Schema'ya göre argümanları doğrula. Hata varsa döndür."""
    props = schema.get("properties", {})
    required = schema.get("required", [])

    for req in required:
        if req not in data:
            return f"Eksik zorunlu parametre: '{req}'"

    for key, value in data.items():
        prop = props.get(key)
        if not prop:
            continue
        prop_type = prop.get("type", "string")
        if prop_type == "string" and not isinstance(value, str):
            return f"'{key}' string olmalı, {type(value).__name__} geldi"
        elif prop_type == "integer" and not isinstance(value, int):
            return f"'{key}' integer olmalı, {type(value).__name__} geldi"
        elif prop_type == "number" and not isinstance(value, (int, float)):
            return f"'{key}' sayı olmalı, {type(value).__name__} geldi"
        elif prop_type == "boolean" and not isinstance(value, bool):
            return f"'{key}' boolean olmalı, {type(value).__name__} geldi"
        elif prop_type == "array" and not isinstance(value, list):
            return f"'{key}' array olmalı, {type(value).__name__} geldi"
        elif prop_type == "object" and not isinstance(value, dict):
            return f"'{key}' object olmalı, {type(value).__name__} geldi"
        # Enum kontrolü
        if "enum" in prop and value not in prop["enum"]:
            return f"'{key}' geçersiz değer: {value}. İzin verilenler: {prop['enum']}"

    return None


# ── Tool Registry ────────────────────────────────────────────────────────

_TOOLS: dict[str, dict] = {}
_HANDLERS: dict[str, Callable] = {}

def tool_kaydet(name: str, description: str, input_schema: dict,
                handler: Callable[[dict], str]) -> None:
    """Bir MCP tool'u kaydet.

    Args:
        name: Tool adı (örn "ReYMeN_run")
        description: Tool açıklaması
        input_schema: JSON Schema
        handler: Args dict alır, str döndürür
    """
    _TOOLS[name] = {"name": name, "description": description,
                     "inputSchema": input_schema}
    _HANDLERS[name] = handler
    logger.info("MCP tool kaydedildi: %s", name)


def tool_sil(name: str) -> bool:
    if name in _TOOLS:
        del _TOOLS[name]
        del _HANDLERS[name]
        return True
    return False


def get_tools() -> list[dict]:
    return list(_TOOLS.values())


# ── Resources Registry ──────────────────────────────────────────────────

_RESOURCES: dict[str, dict] = {}
_RESOURCE_HANDLERS: dict[str, Callable] = {}

def resource_kaydet(uri: str, name: str, description: str = "",
                    mime_type: str = "text/plain",
                    handler: Callable[[], str] | None = None) -> None:
    """Bir MCP resource kaydet.

    Args:
        uri: Resource URI'si (örn "reymen://status")
        name: Resource adı
        description: Açıklama
        mime_type: MIME tipi
        handler: Resource içeriğini döndüren fonksiyon
    """
    _RESOURCES[uri] = {
        "uri": uri, "name": name, "description": description,
        "mimeType": mime_type,
    }
    if handler:
        _RESOURCE_HANDLERS[uri] = handler
    logger.info("MCP resource kaydedildi: %s (%s)", uri, name)


def resource_sil(uri: str) -> bool:
    if uri in _RESOURCES:
        del _RESOURCES[uri]
        _RESOURCE_HANDLERS.pop(uri, None)
        return True
    return False


def get_resources() -> list[dict]:
    return list(_RESOURCES.values())


def resource_oku(uri: str) -> dict | None:
    """Resource içeriğini oku. {contents: [...]} döndür veya None."""
    meta = _RESOURCES.get(uri)
    if not meta:
        return None
    handler = _RESOURCE_HANDLERS.get(uri)
    text = handler() if handler else f"[Resource: {meta['name']}]"
    return {
        "contents": [{
            "uri": uri, "mimeType": meta["mimeType"], "text": text[:8000],
        }]
    }


# ── Prompts Registry ────────────────────────────────────────────────────

_PROMPTS: dict[str, dict] = {}
_PROMPT_HANDLERS: dict[str, Callable] = {}

def prompt_kaydet(name: str, description: str = "",
                  arguments: list[dict] | None = None,
                  handler: Callable[[dict], str] | None = None) -> None:
    """Bir MCP prompt kaydet.

    Args:
        name: Prompt adı
        description: Açıklama
        arguments: Argüman tanımları [{"name": "...", "description": "...", "required": bool}]
        handler: Args dict alır, prompt mesaj metnini döndürür
    """
    _PROMPTS[name] = {
        "name": name, "description": description,
        "arguments": arguments or [],
    }
    if handler:
        _PROMPT_HANDLERS[name] = handler
    logger.info("MCP prompt kaydedildi: %s", name)


def prompt_sil(name: str) -> bool:
    if name in _PROMPTS:
        del _PROMPTS[name]
        _PROMPT_HANDLERS.pop(name, None)
        return True
    return False


def get_prompts() -> list[dict]:
    return list(_PROMPTS.values())


def prompt_get(name: str, args: dict | None = None) -> dict | None:
    """Prompt mesajlarını oluştur. {messages: [...]} döndür veya None."""
    meta = _PROMPTS.get(name)
    if not meta:
        return None
    handler = _PROMPT_HANDLERS.get(name)
    text = handler(args or {}) if handler else f"[Prompt: {meta['description']}]"
    return {
        "messages": [{"role": "user", "content": {"type": "text", "text": text}}]
    }


# ── Roots Registry ──────────────────────────────────────────────────────

_ROOTS: list[dict] = []
_ROOT_WATCHERS: list[str] = []

def root_ekle(uri: str, name: str = "") -> None:
    """Root (dosya sistemi kökü) ekle."""
    _ROOTS.append({"uri": uri, "name": name or uri})
    roots_changed_notify_all()


def root_sil(uri: str) -> bool:
    for r in list(_ROOTS):
        if r["uri"] == uri:
            _ROOTS.remove(r)
            roots_changed_notify_all()
            return True
    return False


def get_roots() -> list[dict]:
    return list(_ROOTS)


# ── Session Management ──────────────────────────────────────────────────

class ClientSession:
    """Bağlı bir MCP client'ının oturumu."""

    def __init__(self, client_id: str, transport: str):
        self.id = client_id
        self.transport = transport
        self.connected_at = time.time()
        self.last_activity = time.time()
        self.initialized = False
        self.client_info: dict = {}
        self.root_watcher = False  # roots/list_changed notification istiyor mu

    @property
    def duration(self) -> float:
        return time.time() - self.connected_at

    def touch(self) -> None:
        self.last_activity = time.time()

    def as_dict(self) -> dict:
        return {
            "id": self.id, "transport": self.transport,
            "connected_at": self.connected_at,
            "last_activity": self.last_activity,
            "initialized": self.initialized,
            "client_info": self.client_info,
            "duration_seconds": round(self.duration, 1),
        }


_SESSIONS: dict[str, ClientSession] = {}
_SESSION_LOCK = threading.Lock()


def _session_ac(client_id: str | None = None, transport: str = "stdio") -> ClientSession:
    with _SESSION_LOCK:
        sid = client_id or f"client_{uuid.uuid4().hex[:8]}"
        session = ClientSession(sid, transport)
        _SESSIONS[sid] = session
        return session


def _session_bul(client_id: str) -> ClientSession | None:
    with _SESSION_LOCK:
        return _SESSIONS.get(client_id)


def _session_kapat(client_id: str) -> None:
    with _SESSION_LOCK:
        _SESSIONS.pop(client_id, None)


def get_sessions() -> list[dict]:
    with _SESSION_LOCK:
        return [s.as_dict() for s in _SESSIONS.values()]


def roots_changed_notify_all() -> None:
    """roots/list_changed notification'ını tüm watcher'lara gönder."""
    pass  # Transport implementasyonunda override edilir


# ── Varsayılan Tool'lar ─────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent.parent


def _tool_status(args: dict) -> str:
    return json.dumps({
        "calisiyor": False, "version": SERVER_INFO["version"],
        "tool_sayisi": len(_TOOLS), "resource_sayisi": len(_RESOURCES),
        "prompt_sayisi": len(_PROMPTS), "session_sayisi": len(get_sessions()),
        "python": sys.version.split()[0], "platform": sys.platform,
    }, ensure_ascii=False)


def _tool_memory_search(args: dict) -> str:
    sorgu = args.get("sorgu", "")
    try:
        from reymen.core.ogrenme import istatistik
        return json.dumps({"sorgu": sorgu,
                            "ogrenme_istatistik": istatistik()},
                           ensure_ascii=False)
    except Exception as e:
        return f"Hafiza arama hatasi: {e}"


def _tool_session_search(args: dict) -> str:
    sorgu = args.get("sorgu", "")
    limit = args.get("limit", 10)
    try:
        from reymen.core.session_search import session_ara
        return json.dumps(session_ara(sorgu, limit=limit), ensure_ascii=False)
    except Exception as e:
        return f"Session arama hatasi: {e}"


def _tool_learning_stats(args: dict) -> str:
    try:
        from reymen.core.ogrenme import istatistik, eski_basarisizlari_temizle
        eski_basarisizlari_temizle()
        return json.dumps(istatistik(), ensure_ascii=False)
    except Exception as e:
        return f"Istatistik hatasi: {e}"


def _tool_file_read(args: dict) -> str:
    dosya = args.get("dosya", "")
    yol = Path(dosya) if Path(dosya).is_absolute() else ROOT / dosya
    if not yol.exists():
        return f"Dosya bulunamadi: {dosya}"
    # Root güvenlik kontrolü
    if not _root_icinde_mi(yol):
        return f"Erisim reddedildi: {dosya} root dizininda degil"
    try:
        return yol.read_text(encoding="utf-8")[:8000]
    except Exception as e:
        return f"Okuma hatasi: {e}"


def _tool_file_write(args: dict) -> str:
    dosya = args.get("dosya", "")
    icerik = args.get("icerik", "")
    yol = Path(dosya) if Path(dosya).is_absolute() else ROOT / dosya
    if not _root_icinde_mi(yol):
        if not _rootlarda_mi(yol):
            return f"Erisim reddedildi: {dosya} root dizininda degil"
    try:
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(icerik, encoding="utf-8")
        return f"Yazildi: {dosya} ({len(icerik)} karakter)"
    except Exception as e:
        return f"Yazma hatasi: {e}"


def _tool_shell(args: dict) -> str:
    import shlex, subprocess
    komut = args.get("komut", "")
    try:
        args_list = shlex.split(komut, posix=(sys.platform != "win32"))
        if not args_list:
            return "Gecersiz komut"
        r = subprocess.run(
            args_list, shell=False, capture_output=True, text=True,
            cwd=str(ROOT), timeout=60,
        )
        return (r.stdout + r.stderr)[:4000]
    except subprocess.TimeoutExpired:
        return "Zaman asimi (60s)"
    except Exception as e:
        return f"Hata: {e}"


def _root_icinde_mi(yol: Path) -> bool:
    """Dosya proje root'u içinde mi?"""
    try:
        return ROOT in yol.parents or yol == ROOT
    except ValueError:
        return False


def _rootlarda_mi(yol: Path) -> bool:
    """Dosya kayıtlı root'lardan birinin altında mı?"""
    for r in _ROOTS:
        try:
            rp = Path(r["uri"].replace("file://", ""))
            if rp in yol.parents or yol == rp:
                return True
        except Exception:
            continue
    return False


def _varsayilan_toollari_kaydet() -> None:
    """ReYMeN'in temel tool'larını MCP olarak kaydet."""
    tool_kaydet("ReYMeN_status", "ReYMeN ajan durumu.",
                {"type": "object", "properties": {}}, _tool_status)
    tool_kaydet("ReYMeN_memory_search", "Anlamsal hafizada ara.",
                {"type": "object", "properties": {
                    "sorgu": {"type": "string", "description": "Arama sorgusu"}},
                 "required": ["sorgu"]}, _tool_memory_search)
    tool_kaydet("ReYMeN_session_search", "Gecmis session larda FTS5 ara.",
                {"type": "object", "properties": {
                    "sorgu": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}},
                 "required": ["sorgu"]}, _tool_session_search)
    tool_kaydet("ReYMeN_learning_stats", "Ogrenme istatistikleri.",
                {"type": "object", "properties": {}}, _tool_learning_stats)
    tool_kaydet("ReYMeN_file_read", "Proje dizininde dosya oku.",
                {"type": "object", "properties": {
                    "dosya": {"type": "string", "description": "Dosya yolu"}},
                 "required": ["dosya"]}, _tool_file_read)
    tool_kaydet("ReYMeN_file_write", "Proje dizininde dosyaya yaz.",
                {"type": "object", "properties": {
                    "dosya": {"type": "string"},
                    "icerik": {"type": "string"}},
                 "required": ["dosya", "icerik"]}, _tool_file_write)
    tool_kaydet("ReYMeN_shell", "Guvenli kabuk komutu.",
                {"type": "object", "properties": {
                    "komut": {"type": "string"}},
                 "required": ["komut"]}, _tool_shell)


def _varsayilan_resources_kaydet() -> None:
    """Varsayılan resource'ları kaydet."""
    resource_kaydet("reymen://status", "ReYMeN Status",
                     "Ajan durum bilgisi", handler=lambda: _tool_status({}))
    resource_kaydet("reymen://tools", "ReYMeN Tools",
                     "Kayitli tool listesi",
                     handler=lambda: json.dumps(get_tools(), indent=2, ensure_ascii=False))
    resource_kaydet("reymen://sessions", "Active Sessions",
                     "Bagli MCP client oturumlari",
                     handler=lambda: json.dumps(get_sessions(), indent=2, ensure_ascii=False))
    resource_kaydet("reymen://roots", "Filesystem Roots",
                     "Dosya sistemi kok dizinleri",
                     handler=lambda: json.dumps(get_roots(), indent=2, ensure_ascii=False))


# ── JSON-RPC İşleyici ───────────────────────────────────────────────────

def _yanit(req_id, sonuc):
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": sonuc})


def _hata_yaniti(req_id, code, mesaj):
    return json.dumps({
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": code, "message": mesaj},
    })


def _istek_isle(istek: dict, session: ClientSession | None = None) -> str | None:
    """Bir JSON-RPC isteğini işle.

    Args:
        istek: JSON-RPC isteği.
        session: Varsa oturum (notifications için).

    Returns:
        JSON yanıt string'i veya None (bildirimse).
    """
    method = istek.get("method", "")
    req_id = istek.get("id")
    params = istek.get("params", {})

    if session:
        session.touch()

    # ── Lifecycle ──────────────────────────────────────────────────────
    if method == "initialize":
        if session:
            session.initialized = True
            session.client_info = params.get("clientInfo", {})

        # Client capabilities'den roots watcher kontrolü
        capabilities = params.get("capabilities", {})
        roots_caps = capabilities.get("roots", {})
        if roots_caps.get("listChanged") and session:
            session.root_watcher = True

        # Varsayılan root ekle
        if not _ROOTS:
            root_ekle(f"file://{ROOT}", "ReYMeN Project Root")

        return _yanit(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": SERVER_INFO,
            "capabilities": {
                "tools": {},
                "resources": {
                    "listChanged": True,
                    "subscribe": True,
                },
                "prompts": {"listChanged": True},
                "roots": {"listChanged": True},
                "logging": {},
            },
        })

    if method == "notifications/initialized":
        # Client initialized bildirimi aldı
        return None

    # ── Tools ──────────────────────────────────────────────────────────
    if method == "tools/list":
        cursor = params.get("cursor")
        tools = get_tools()
        result = {"tools": tools}
        return _yanit(req_id, result)

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})

        if name not in _HANDLERS:
            return _hata_yaniti(req_id, -32601, f"Tool bulunamadi: {name}")

        # Schema doğrulama
        tool_meta = _TOOLS.get(name, {})
        schema = tool_meta.get("inputSchema", {})
        schema_hata = _schema_dogrula(schema, args)
        if schema_hata:
            return _hata_yaniti(req_id, -32602, f"Gecersiz arguman: {schema_hata}")

        try:
            sonuc = _HANDLERS[name](args)
            return _yanit(req_id, {
                "content": [{"type": "text", "text": sonuc}]
            })
        except Exception as e:
            logger.exception("Tool hatasi: %s", name)
            return _hata_yaniti(req_id, -32603, str(e))

    # ── Resources ──────────────────────────────────────────────────────
    if method == "resources/list":
        return _yanit(req_id, {"resources": get_resources()})

    if method == "resources/read":
        uri = params.get("uri", "")
        icerik = resource_oku(uri)
        if icerik is None:
            return _hata_yaniti(req_id, -32602,
                                 f"Resource bulunamadi: {uri}")
        return _yanit(req_id, icerik)

    if method == "resources/subscribe":
        uri = params.get("uri", "")
        if uri not in _RESOURCES:
            return _hata_yaniti(req_id, -32602,
                                 f"Resource bulunamadi: {uri}")
        return _yanit(req_id, {})

    if method == "resources/unsubscribe":
        return _yanit(req_id, {})

    # ── Prompts ────────────────────────────────────────────────────────
    if method == "prompts/list":
        return _yanit(req_id, {"prompts": get_prompts()})

    if method == "prompts/get":
        name = params.get("name", "")
        args = params.get("arguments", {})
        icerik = prompt_get(name, args)
        if icerik is None:
            return _hata_yaniti(req_id, -32602,
                                 f"Prompt bulunamadi: {name}")
        return _yanit(req_id, icerik)

    # ── Roots ──────────────────────────────────────────────────────────
    if method == "roots/list":
        return _yanit(req_id, {"roots": get_roots()})

    # ── Ping / Sağlık ──────────────────────────────────────────────────
    if method == "ping":
        return _yanit(req_id, {})

    # ── Bildirimler ────────────────────────────────────────────────────
    if method.startswith("notifications/"):
        if method == "notifications/roots/list_changed" and session:
            # Client root'ları değişti
            pass
        return None

    return _hata_yaniti(req_id, -32601, f"Method not found: {method}")


# ── Stdio Transport ─────────────────────────────────────────────────────

def stdio_dongu():
    """MCP stdio protokolü: her satır bir JSON-RPC isteği."""
    session = _session_ac(transport="stdio")
    logger.info("MCP Server stdio modunda basladi (session=%s)", session.id)

    try:
        for satir in sys.stdin:
            satir = satir.strip()
            if not satir:
                continue
            try:
                istek = json.loads(satir)
            except json.JSONDecodeError as e:
                yanit = _hata_yaniti(None, -32700, f"Parse error: {e}")
                print(yanit, flush=True)
                continue
            try:
                yanit = _istek_isle(istek, session)
            except Exception as e:
                yanit = _hata_yaniti(istek.get("id"), -32603, str(e))
            if yanit is not None:
                print(yanit, flush=True)
    finally:
        _session_kapat(session.id)
        logger.info("MCP Server stdio kapandi (session=%s)", session.id)


# ── HTTP Transport (Streamable HTTP / SSE) ──────────────────────────────

def http_baslat(host: str = "0.0.0.0", port: int = 9000):
    """HTTP tabanlı MCP sunucusu başlat (FastAPI + SSE)."""
    try:
        import asyncio
        import uvicorn
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse, StreamingResponse
    except ImportError:
        logger.error("fastapi/uvicorn kurulu degil: pip install fastapi uvicorn")
        return

    app = FastAPI(title="ReYMeN MCP Server", version=SERVER_INFO["version"])
    _sse_clients: dict[str, asyncio.Queue] = {}

    @app.get("/health")
    async def saglik():
        return {"status": "ok", "tool_sayisi": len(_TOOLS),
                "session_sayisi": len(get_sessions())}

    @app.get("/mcp/sessions")
    async def session_listele():
        return get_sessions()

    @app.post("/mcp")
    async def mcp_handler(request: Request):
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"jsonrpc": "2.0",
                          "error": {"code": -32700, "message": "Gecersiz JSON"},
                          "id": None},
            )

        # Session yönetimi (HTTP header'dan client_id)
        client_id = request.headers.get("X-MCP-Client-Id", "")
        session = _session_bul(client_id) if client_id else None
        if session is None:
            session = _session_ac(client_id or None, transport="http")
            session.initialized = True

        # SSE event stream isteği mi?
        if body.get("method") == "sse/connect":
            queue: asyncio.Queue = asyncio.Queue()
            _sse_clients[session.id] = queue

            async def event_stream():
                try:
                    # İlk event: endpoint bilgisi
                    yield f"event: endpoint\ndata: {json.dumps({'endpoint': f'http://{host}:{port}/mcp'})}\n\n"
                    while True:
                        try:
                            msg = await asyncio.wait_for(queue.get(), timeout=30)
                            yield f"event: message\ndata: {msg}\n\n"
                        except asyncio.TimeoutError:
                            yield f"event: heartbeat\ndata: {json.dumps({})}\n\n"
                except asyncio.CancelledError:
                    pass
                finally:
                    _sse_clients.pop(session.id, None)
                    _session_kapat(session.id)

            return StreamingResponse(event_stream(), media_type="text/event-stream",
                                       headers={
                                           "Cache-Control": "no-cache",
                                           "Connection": "keep-alive",
                                           "X-Accel-Buffering": "no",
                                       })

        # Normal JSON-RPC
        yanit = _istek_isle(body, session)
        if yanit is None:
            return {"jsonrpc": "2.0", "result": {}, "id": body.get("id")}
        result = json.loads(yanit)

        return JSONResponse(content=result)

    logger.info("MCP Server HTTP modunda basliyor: %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


# ── CLI Giriş ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ReYMeN MCP Server")
    parser.add_argument("--transport", choices=["stdio", "http"],
                        default="stdio", help="Transport tipi")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=9000, help="HTTP port")
    args = parser.parse_args()

    _varsayilan_toollari_kaydet()
    _varsayilan_resources_kaydet()

    logging.basicConfig(level=logging.INFO,
                        format="[MCP %(asctime)s] %(message)s")

    if args.transport == "stdio":
        stdio_dongu()
    else:
        http_baslat(args.host, args.port)


# ── Motor Entegrasyonu ──────────────────────────────────────────────────

def motor_kaydet(motor) -> None:
    """Motor'a MCP server başlatma/kontrol araçlarını kaydet.

    Args:
        motor: Motor instance'ı.
    """
    motor._plugin_arac_kaydet(
        "MCP_SERVER_BASLAT", _mcp_baslat,
        "MCP sunucusunu baslat. Parametreler: transport (str, stdio/http), "
        "port (int, varsayilan 9000). Background'ta calisir."
    )
    motor._plugin_arac_kaydet(
        "MCP_SERVER_DURUM", _mcp_durum,
        "MCP sunucu durumu: tool/resource/prompt/session sayilari."
    )
    motor._plugin_arac_kaydet(
        "MCP_TOOL_EKLE", _mcp_tool_ekle,
        "Calisma zamaninda MCP tool ekle. Parametreler: name (str), "
        "description (str), input_schema (str: JSON), handler_turu (str: builtin/custom)"
    )
    motor._plugin_arac_kaydet(
        "MCP_RESOURCE_EKLE", _mcp_resource_ekle,
        "MCP resource ekle. Parametreler: uri (str), name (str), "
        "description (str), mime_type (str)"
    )
    motor._plugin_arac_kaydet(
        "MCP_ROOT_EKLE", _mcp_root_ekle,
        "MCP filesystem root ekle. Parametreler: path (str, absolute)"
    )
    logger.info("[MCP] Motor'a 5 arac kaydedildi")


def _mcp_baslat(transport: str = "stdio", port: int = 9000) -> str:
    """MCP sunucusunu background thread'de başlat."""
    import threading as _t
    _varsayilan_toollari_kaydet()
    _varsayilan_resources_kaydet()

    if transport == "http":
        def _run():
            http_baslat(port=port)
        t = _t.Thread(target=_run, daemon=True)
        t.start()
        return f"[MCP] HTTP sunucu baslatildi: port={port}"
    else:
        return ("[MCP] Stdio modu icin: "
                "python -m reymen.core.mcp_server --transport stdio")


def _mcp_durum(**kw) -> str:
    """MCP sunucu durum raporu."""
    return json.dumps({
        "tools": len(_TOOLS),
        "resources": len(_RESOURCES),
        "prompts": len(_PROMPTS),
        "roots": len(_ROOTS),
        "sessions": len(get_sessions()),
        "protocol": PROTOCOL_VERSION,
        "server": SERVER_INFO,
    }, indent=2, ensure_ascii=False)


def _mcp_tool_ekle(name: str, description: str = "",
                    input_schema: str = "{}",
                    handler_turu: str = "builtin") -> str:
    """Çalışma zamanında MCP tool ekle."""
    try:
        schema = json.loads(input_schema)
    except json.JSONDecodeError:
        return "[MCP] Gecersiz input_schema JSON"

    if handler_turu == "builtin":
        # Bilinen handler'lara yönlendir
        handler_map = {
            "status": _tool_status,
            "file_read": _tool_file_read,
            "file_write": _tool_file_write,
            "shell": _tool_shell,
            "memory_search": _tool_memory_search,
            "session_search": _tool_session_search,
            "learning_stats": _tool_learning_stats,
        }
        handler = handler_map.get(name.split("_")[-1] if "_" in name else name)
        if handler is None:
            return (f"[MCP] Bilinmeyen handler: {name}. "
                    f"Kullanilabilirler: {list(handler_map.keys())}")
    else:
        return "[MCP] Custom handler su an desteklenmiyor"

    tool_kaydet(name, description, schema, handler)
    return f"[MCP] Tool eklendi: {name}"


def _mcp_resource_ekle(uri: str, name: str, description: str = "",
                        mime_type: str = "text/plain") -> str:
    """Çalışma zamanında MCP resource ekle."""
    resource_kaydet(uri, name, description, mime_type)
    return f"[MCP] Resource eklendi: {uri} ({name})"


def _mcp_root_ekle(path: str) -> str:
    """Filesystem root ekle."""
    p = Path(path)
    if not p.exists():
        return f"[MCP] Path bulunamadi: {path}"
    root_ekle(f"file://{p.resolve()}", p.name)
    return f"[MCP] Root eklendi: {p.resolve()}"


if __name__ == "__main__":
    main()
