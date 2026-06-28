# -*- coding: utf-8 -*-
"""
reymen/core/mcp_server.py — ReYMeN MCP Server Host.

ReYMeN'i bir MCP (Model Context Protocol) sunucusu olarak yayınlar.
Diğer MCP client'ları (Claude Code, Cursor, Windsurf vb.) buraya bağlanıp
ReYMeN'in tool'larını çağırabilir.

Stdio ve HTTP (SSE) transport destekler.

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
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── MCP Protokol Sabitleri ───────────────────────────────────────────
PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {"name": "ReYMeN", "version": "2.0.0"}

# ── Tool Registry ────────────────────────────────────────────────────

_TOOLS: Dict[str, Dict[str, Any]] = {}
_HANDLERS: Dict[str, Callable] = {}


def tool_kaydet(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    handler: Callable[[Dict[str, Any]], str],
):
    """Bir MCP tool'u kaydet.

    Args:
        name: Tool adı (örn "ReYMeN_run")
        description: Tool açıklaması
        input_schema: JSON Schema formatında parametre tanımı
        handler: Tool çağrıldığında çalışacak fonksiyon (args dict alır, str döndürür)
    """
    _TOOLS[name] = {
        "name": name,
        "description": description,
        "inputSchema": input_schema,
    }
    _HANDLERS[name] = handler
    logger.info("MCP tool kaydedildi: %s", name)


def tool_sil(name: str) -> bool:
    """Bir tool'u sil."""
    if name in _TOOLS:
        del _TOOLS[name]
        del _HANDLERS[name]
        return True
    return False


def get_tools() -> List[Dict[str, Any]]:
    """Tüm kayıtlı tool'ları listele."""
    return list(_TOOLS.values())


# ── Varsayılan Tool'lar ──────────────────────────────────────────────

def _varsayilan_toollari_kaydet():
    """ReYMeN'in temel tool'larını MCP olarak kaydet."""

    # ReYMeN_status
    tool_kaydet(
        "ReYMeN_status",
        "ReYMeN ajanının mevcut durumunu sorgula.",
        {"type": "object", "properties": {}},
        _tool_status,
    )

    # ReYMeN_memory_search
    tool_kaydet(
        "ReYMeN_memory_search",
        "ReYMeN anlamsal hafızasında arama yap.",
        {
            "type": "object",
            "properties": {
                "sorgu": {"type": "string", "description": "Arama sorgusu"}
            },
            "required": ["sorgu"],
        },
        _tool_memory_search,
    )

    # ReYMeN_session_search
    tool_kaydet(
        "ReYMeN_session_search",
        "Geçmiş session mesajlarında full-text arama yap (FTS5).",
        {
            "type": "object",
            "properties": {
                "sorgu": {"type": "string", "description": "Arama sorgusu"},
                "limit": {"type": "integer", "description": "Maksimum sonuç sayısı", "default": 10},
            },
            "required": ["sorgu"],
        },
        _tool_session_search,
    )

    # ReYMeN_learning_stats
    tool_kaydet(
        "ReYMeN_learning_stats",
        "ReYMeN öğrenme döngüsü istatistiklerini getir.",
        {"type": "object", "properties": {}},
        _tool_learning_stats,
    )

    # ReYMeN_file_read
    tool_kaydet(
        "ReYMeN_file_read",
        "Proje dizininde bir dosyayı oku.",
        {
            "type": "object",
            "properties": {
                "dosya": {"type": "string", "description": "Dosya yolu"}
            },
            "required": ["dosya"],
        },
        _tool_file_read,
    )

    # ReYMeN_file_write
    tool_kaydet(
        "ReYMeN_file_write",
        "Proje dizininde bir dosyaya yaz.",
        {
            "type": "object",
            "properties": {
                "dosya": {"type": "string"},
                "icerik": {"type": "string"},
            },
            "required": ["dosya", "icerik"],
        },
        _tool_file_write,
    )

    # ReYMeN_shell
    tool_kaydet(
        "ReYMeN_shell",
        "Proje dizininde güvenli kabuk komutu çalıştır (shlex.split, shell=False).",
        {
            "type": "object",
            "properties": {
                "komut": {"type": "string", "description": "Shell komutu"}
            },
            "required": ["komut"],
        },
        _tool_shell,
    )


# ── Tool Handler'ları ────────────────────────────────────────────────

ROOT = Path(__file__).parent.parent.parent.resolve()


def _tool_status(args: Dict[str, Any]) -> str:
    """Ajan durumunu döndür."""
    return json.dumps({
        "calisiyor": False,
        "version": SERVER_INFO["version"],
        "tool_sayisi": len(_TOOLS),
        "python": sys.version.split()[0],
        "platform": sys.platform,
    }, ensure_ascii=False)


def _tool_memory_search(args: Dict[str, Any]) -> str:
    """Anlamsal hafızada ara."""
    sorgu = args.get("sorgu", "")
    try:
        from reymen.core.ogrenme import istatistik
        stats = istatistik()
        return json.dumps({
            "sorgu": sorgu,
            "ogrenme_istatistik": stats,
            "not": "Detaylı vektörel hafıza için reymen.hafiza.vektorel_hafiza kullanın",
        }, ensure_ascii=False)
    except Exception as e:
        return f"Hafıza arama hatası: {e}"


def _tool_session_search(args: Dict[str, Any]) -> str:
    """Session mesajlarında FTS5 ile ara."""
    sorgu = args.get("sorgu", "")
    limit = args.get("limit", 10)
    try:
        from reymen.core.session_search import session_ara
        sonuclar = session_ara(sorgu, limit=limit)
        return json.dumps(sonuclar, ensure_ascii=False)
    except Exception as e:
        return f"Session arama hatası: {e}"


def _tool_learning_stats(args: Dict[str, Any]) -> str:
    """Öğrenme istatistikleri."""
    try:
        from reymen.core.ogrenme import istatistik, eski_basarisizlari_temizle
        eski_basarisizlari_temizle()
        stats = istatistik()
        return json.dumps(stats, ensure_ascii=False)
    except Exception as e:
        return f"İstatistik hatası: {e}"


def _tool_file_read(args: Dict[str, Any]) -> str:
    """Dosya oku."""
    dosya = args.get("dosya", "")
    yol = Path(dosya) if Path(dosya).is_absolute() else ROOT / dosya
    if not yol.exists():
        return f"Dosya bulunamadı: {dosya}"
    try:
        return yol.read_text(encoding="utf-8")[:8000]
    except Exception as e:
        return f"Okuma hatası: {e}"


def _tool_file_write(args: Dict[str, Any]) -> str:
    """Dosyaya yaz."""
    dosya = args.get("dosya", "")
    icerik = args.get("icerik", "")
    yol = Path(dosya) if Path(dosya).is_absolute() else ROOT / dosya
    try:
        yol.parent.mkdir(parents=True, exist_ok=True)
        yol.write_text(icerik, encoding="utf-8")
        return f"Yazıldı: {dosya} ({len(icerik)} karakter)"
    except Exception as e:
        return f"Yazma hatası: {e}"


def _tool_shell(args: Dict[str, Any]) -> str:
    """Güvenli shell komutu çalıştır."""
    import subprocess
    import shlex
    komut = args.get("komut", "")
    try:
        args_list = shlex.split(komut, posix=(sys.platform != "win32"))
        if not args_list:
            return "Geçersiz komut"
        r = subprocess.run(  # nosec B603
            args_list, shell=False, capture_output=True, text=True,
            cwd=str(ROOT), timeout=60,
        )
        return (r.stdout + r.stderr)[:4000]
    except subprocess.TimeoutExpired:
        return "Zaman aşımı (60s)"
    except (ValueError, OSError) as e:
        return f"Komut ayrıştırma hatası: {e}"
    except Exception as e:
        return f"Hata: {e}"


# ── JSON-RPC İşleyici ────────────────────────────────────────────────

def _yanit(req_id, sonuc):
    return json.dumps({"jsonrpc": "2.0", "id": req_id, "result": sonuc})


def _hata_yaniti(req_id, code, mesaj):
    return json.dumps({
        "jsonrpc": "2.0", "id": req_id,
        "error": {"code": code, "message": mesaj},
    })


def _istek_isle(istek: dict) -> Optional[str]:
    """Bir JSON-RPC isteğini işle."""
    method = istek.get("method", "")
    req_id = istek.get("id")
    params = istek.get("params", {})

    if method == "initialize":
        return _yanit(req_id, {
            "protocolVersion": PROTOCOL_VERSION,
            "serverInfo": SERVER_INFO,
            "capabilities": {"tools": {}},
        })

    if method == "tools/list":
        return _yanit(req_id, {"tools": get_tools()})

    if method == "tools/call":
        name = params.get("name", "")
        args = params.get("arguments", {})
        if name not in _HANDLERS:
            return _hata_yaniti(req_id, -32601, f"Tool bulunamadı: {name}")
        try:
            sonuc = _HANDLERS[name](args)
            return _yanit(req_id, {
                "content": [{"type": "text", "text": sonuc}]
            })
        except Exception as e:
            logger.exception("Tool hatası: %s", name)
            return _hata_yaniti(req_id, -32603, str(e))

    if method == "ping":
        return _yanit(req_id, {})

    # Bildirimler (id yok, yanıt beklenmez)
    if method.startswith("notifications/"):
        return None

    return _hata_yaniti(req_id, -32601, f"Method not found: {method}")


# ── Stdio Transport ──────────────────────────────────────────────────

def stdio_dongu():
    """MCP stdio protokolü: her satır bir JSON-RPC isteği."""
    logger.info("MCP Server stdio modunda başladı")
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
            yanit = _istek_isle(istek)
        except Exception as e:
            yanit = _hata_yaniti(istek.get("id"), -32603, str(e))
        if yanit is not None:
            print(yanit, flush=True)


# ── HTTP Transport (SSE) ─────────────────────────────────────────────

def http_baslat(host: str = "0.0.0.0", port: int = 9000):
    """HTTP tabanlı MCP sunucusu başlat (FastAPI)."""
    try:
        import uvicorn
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse
    except ImportError:
        logger.error("fastapi/uvicorn kurulu değil: pip install fastapi uvicorn")
        return

    app = FastAPI(
        title="ReYMeN MCP Server",
        version=SERVER_INFO["version"],
    )

    @app.get("/health")
    async def saglik():
        return {"status": "ok", "tool_sayisi": len(_TOOLS)}

    @app.post("/mcp")
    async def mcp_handler(request: Request):
        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                status_code=400,
                content={"jsonrpc": "2.0", "error": {"code": -32700, "message": "Geçersiz JSON"}, "id": None},
            )

        yanit = _istek_isle(body)
        if yanit is None:
            return {"jsonrpc": "2.0", "result": {}, "id": body.get("id")}
        return json.loads(yanit)

    logger.info("MCP Server HTTP modunda başlıyor: %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


# ── Ana Giriş ────────────────────────────────────────────────────────

def main():
    """CLI giriş noktası."""
    parser = argparse.ArgumentParser(description="ReYMeN MCP Server")
    parser.add_argument(
        "--transport", choices=["stdio", "http"], default="stdio",
        help="Transport tipi (varsayılan: stdio)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="HTTP host")
    parser.add_argument("--port", type=int, default=9000, help="HTTP port")
    args = parser.parse_args()

    # Varsayılan tool'ları kaydet
    _varsayilan_toollari_kaydet()

    logging.basicConfig(level=logging.INFO, format="[MCP %(asctime)s] %(message)s")

    if args.transport == "stdio":
        stdio_dongu()
    else:
        http_baslat(args.host, args.port)


if __name__ == "__main__":
    main()