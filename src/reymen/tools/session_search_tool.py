# -*- coding: utf-8 -*-
# Apache 2.0 — ReYMeN Session Search Tool (Hermes'ten uyarlanmistir)
"""
session_search_tool.py — ReYMeN Session Search Tool

ReYMeN'in kendi ``src/reymen/hafiza/session_search.db`` (SQLite FTS5)
veritabanini kullanarak gecmis konusmalarda arama yapar.

DORT KULLANIM SEKLI (parametreden algilanir):
  1. ARAMA — ``query`` gonder. FTS5 ile tara, eslesen session'lari dondur.
  2. KAYDIR — ``session_id`` + ``around_message_id``. Belirli bir mesaj
     etrafindaki pencereyi goster.
  3. OKU — sadece ``session_id``. Session'un tamamini dok (buyukse ilk 20 + son 10).
  4. GOSTER — parametre yok. Son session'lari listele.

Hermes Agent ``tools/session_search_tool.py`` dosyasindan uyarlanmistir
(ReYMeN'in kendi DB ve registry'sine baglanacak sekilde sadeleistirildi).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sabitler
# ---------------------------------------------------------------------------
_DB_PATH = Path(__file__).resolve().parent.parent / "hafiza" / "session_search.db"
_DEFAULT_LIMIT = 3
_MAX_LIMIT = 10
_DEFAULT_WINDOW = 5
_MAX_WINDOW = 20
_HIDDEN_SOURCES = ("subagent", "tool", "delegation")


# ---------------------------------------------------------------------------
# DB baglantisi
# ---------------------------------------------------------------------------
def _baglan() -> sqlite3.Connection:
    """Session search DB'sine baglan. Yoksa None doner."""
    if not _DB_PATH.exists():
        logger.warning("Session search DB bulunamadi: %s", _DB_PATH)
        return None
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Yardimcilar
# ---------------------------------------------------------------------------
def _zaman_damgasi(ts: Union[int, float, str, None]) -> str:
    """Unix timestamp veya ISO string'i insan okunabilir tarihe cevir."""
    if ts is None:
        return "bilinmiyor"
    try:
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts)
            return dt.strftime("%d.%m.%Y %H:%M")
        if isinstance(ts, str):
            # Sayisal string mi?
            cleaned = ts.replace(".", "").replace("-", "").replace(":", "").replace("T", "").replace(" ", "")
            if cleaned.isdigit():
                try:
                    dt = datetime.fromtimestamp(float(ts))
                    return dt.strftime("%d.%m.%Y %H:%M")
                except (ValueError, OSError):
                    return ts[:19]
            return ts[:19]
    except Exception:
        logger.debug("Zaman damgasi donusturulemedi: %s", ts, exc_info=True)
    return str(ts)


def _mesaj_sekillendir(m: Dict[str, Any], anchor_id: Optional[int] = None) -> Dict[str, Any]:
    """Mesaj satirini tool cevabi icin sekillendir."""
    entry = {
        "id": m.get("id"),
        "role": m.get("role"),
        "content": m.get("content"),
        "timestamp": m.get("timestamp"),
    }
    if anchor_id is not None and m.get("id") == anchor_id:
        entry["anchor"] = True
    return {k: v for k, v in entry.items() if v is not None}


def _hata_cevap(mesaj: str, basarili: bool = False) -> str:
    """Hata JSON cevabi."""
    return json.dumps({"success": basarili, "error": mesaj}, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Arama (Discovery) — FTS5
# ---------------------------------------------------------------------------
def _ara(conn: sqlite3.Connection, query: str, limit: int, sort: Optional[str]) -> str:
    """FTS5 ile session'larda ara. Sonuclari session_id bazinda grupla."""
    if conn is None:
        return _hata_cevap("Session DB baglanamadi")

    try:
        # FTS5 sorgusu — MATCH
        sql = """
            SELECT rowid, session_id, message, role, timestamp
            FROM session_messages_fts
            WHERE session_messages_fts MATCH ?
            ORDER BY rowid DESC
        """
        cur = conn.execute(sql, (query,))
        rows = cur.fetchall()
    except Exception as e:
        logger.error("FTS5 arama hatasi: %s", e, exc_info=True)
        return _hata_cevap(f"Arama basarisiz: {e}")

    if not rows:
        return json.dumps({
            "success": True, "mode": "discover",
            "query": query, "results": [], "count": 0,
            "message": "Eslesen session bulunamadi.",
        }, ensure_ascii=False)

    # Session_ID bazinda grupla (ilk eslesmeyi tut)
    seen: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        sid = r["session_id"]
        if sid not in seen and len(seen) < limit:
            seen[sid] = {
                "session_id": sid,
                "match_message_id": r["rowid"],
                "matched_role": r["role"],
                "snippet": (r["message"] or "")[:200],
                "timestamp": r["timestamp"],
                "session_messages": [],
            }

    # Her session icin pencere + kitap uclari topla
    results = []
    for sid, info in seen.items():
        try:
            msg_rows = conn.execute(
                "SELECT rowid, session_id, message, role, timestamp "
                "FROM session_messages_fts WHERE session_id = ? "
                "ORDER BY rowid ASC",
                (sid,),
            ).fetchall()
        except Exception:
            continue

        msgs = [{"id": r["rowid"], "role": r["role"], "content": r["message"], "timestamp": r["timestamp"]} for r in msg_rows]
        total = len(msgs)
        match_idx = next((i for i, m in enumerate(msgs) if m["id"] == info["match_message_id"]), -1)

        # Kitap uclari (ilk 3 + son 3)
        bookend_start = msgs[:3] if total > 6 else msgs[:1]
        bookend_end = msgs[-3:] if total > 3 else msgs[-1:]

        # Pencere (±5)
        if match_idx >= 0:
            lo = max(0, match_idx - 5)
            hi = min(total, match_idx + 6)
            window = msgs[lo:hi]
        else:
            window = msgs[:5]

        results.append({
            "session_id": sid,
            "when": _zaman_damgasi(info["timestamp"]),
            "snippet": info["snippet"],
            "match_message_id": info["match_message_id"],
            "matched_role": info["matched_role"],
            "message_count": total,
            "bookend_start": bookend_start,
            "messages": window,
            "bookend_end": bookend_end,
        })

    return json.dumps({
        "success": True, "mode": "discover",
        "query": query, "results": results,
        "count": len(results),
        "sessions_searched": len(seen),
    }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Goster (Browse) — son session'lari listele
# ---------------------------------------------------------------------------
def _son_sessionlar(conn: sqlite3.Connection, limit: int) -> str:
    """En son kullanilan session'lari listele."""
    if conn is None:
        return _hata_cevap("Session DB baglanamadi")

    try:
        rows = conn.execute(
            "SELECT session_id, COUNT(*) as cnt, "
            "MIN(rowid) as first_rowid, MAX(rowid) as last_rowid, "
            "MIN(timestamp) as first_ts, MAX(timestamp) as last_ts "
            "FROM session_messages_fts "
            "GROUP BY session_id "
            "ORDER BY last_rowid DESC "
            "LIMIT ?",
            (limit + 5,),
        ).fetchall()
    except Exception as e:
        logger.error("Session listeleme hatasi: %s", e, exc_info=True)
        return _hata_cevap(f"Session listeleme basarisiz: {e}")

    results = []
    for r in rows:
        # Ilk mesaji al (preview / baslik)
        preview = ""
        try:
            first = conn.execute(
                "SELECT message FROM session_messages_fts WHERE session_id = ? ORDER BY rowid ASC LIMIT 1",
                (r["session_id"],),
            ).fetchone()
            if first:
                preview = (first["message"] or "")[:100]
        except Exception:
            pass

        results.append({
            "session_id": r["session_id"],
            "message_count": r["cnt"],
            "started_at": _zaman_damgasi(r["first_ts"]),
            "last_active": _zaman_damgasi(r["last_ts"]),
            "preview": preview,
        })

    return json.dumps({
        "success": True, "mode": "browse",
        "results": results[:limit],
        "count": min(len(results), limit),
        "message": f"Son {len(results[:limit])} session gosteriliyor.",
    }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Kaydir (Scroll) — belirli bir mesaj etrafinda pencere
# ---------------------------------------------------------------------------
def _kaydir(conn: sqlite3.Connection, session_id: str, around_message_id: int, window: int) -> str:
    """Bir mesaj etrafinda ±window kadar mesaj goster."""
    if conn is None:
        return _hata_cevap("Session DB baglanamadi")

    window = max(1, min(window, _MAX_WINDOW))

    try:
        # Once bu session'daki tum mesajlari sirala
        rows = conn.execute(
            "SELECT rowid, session_id, message, role, timestamp "
            "FROM session_messages_fts WHERE session_id = ? "
            "ORDER BY rowid ASC",
            (session_id,),
        ).fetchall()
    except Exception as e:
        return _hata_cevap(f"Session mesajlari yuklenemedi: {e}")

    if not rows:
        return _hata_cevap(f"Session bulunamadi: {session_id}")

    # Hedef mesajin index'ini bul
    msgs = [dict(r) for r in rows]
    match_idx = next((i for i, m in enumerate(msgs) if m["rowid"] == around_message_id), -1)

    if match_idx < 0:
        return _hata_cevap(f"around_message_id {around_message_id} session {session_id} icinde bulunamadi")

    lo = max(0, match_idx - window)
    hi = min(len(msgs), match_idx + window + 1)
    window_msgs = [_mesaj_sekillendir({"id": m["rowid"], "role": m["role"], "content": m["message"], "timestamp": m["timestamp"]}, anchor_id=around_message_id) for m in msgs[lo:hi]]

    return json.dumps({
        "success": True, "mode": "scroll",
        "session_id": session_id,
        "around_message_id": around_message_id,
        "window": window,
        "messages_before": match_idx - lo,
        "messages_after": hi - match_idx - 1,
        "messages": window_msgs,
    }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Oku (Read) — session'un tamamini dok
# ---------------------------------------------------------------------------
def _oku(conn: sqlite3.Connection, session_id: str, head: int = 20, tail: int = 10) -> str:
    """Session'un tum mesajlarini goster (buyukse head + tail)."""
    if conn is None:
        return _hata_cevap("Session DB baglanamadi")

    try:
        rows = conn.execute(
            "SELECT rowid, session_id, message, role, timestamp "
            "FROM session_messages_fts WHERE session_id = ? "
            "ORDER BY rowid ASC",
            (session_id,),
        ).fetchall()
    except Exception as e:
        return _hata_cevap(f"Session yuklenemedi: {e}")

    if not rows:
        return _hata_cevap(f"Session bulunamadi: {session_id}")

    msgs = [_mesaj_sekillendir({"id": r["rowid"], "role": r["role"], "content": r["message"], "timestamp": r["timestamp"]}) for r in rows]
    total = len(msgs)
    truncated = total > head + tail
    window = msgs[:head] + msgs[-tail:] if truncated else msgs

    return json.dumps({
        "success": True, "mode": "read",
        "session_id": session_id,
        "message_count": total,
        "truncated": truncated,
        "messages": window,
        "message": f"Session {total} mesaj iceriyor; ilk {head} + son {tail} gosteriliyor." if truncated else None,
    }, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Ana fonksiyon — 4 kullanim seklini parametrelerden algila
# ---------------------------------------------------------------------------
def session_search(
    query: str = "",
    limit: int = _DEFAULT_LIMIT,
    session_id: str = None,
    around_message_id: int = None,
    window: int = _DEFAULT_WINDOW,
    sort: str = None,
    **kwargs,
) -> str:
    """Session Search Tool.

    4 kullanim sekli:
    1. Arama: query='aranan kelime'
    2. Kaydir: session_id='...', around_message_id=12345
    3. Oku: session_id='...' (around_message_id olmadan)
    4. Goster: parametresiz
    """
    conn = _baglan()
    if conn is None:
        return _hata_cevap("Session search veritabanina baglanilamadi. DB henuz olusturulmamis olabilir.")

    try:
        # Kaydir: session_id + around_message_id
        if session_id and session_id.strip() and around_message_id is not None:
            return _kaydir(conn, session_id.strip(), around_message_id, window)

        # Oku: sadece session_id
        if session_id and session_id.strip():
            return _oku(conn, session_id.strip())

        # Limit kontrol
        if not isinstance(limit, int):
            try:
                limit = int(limit)
            except (TypeError, ValueError):
                limit = _DEFAULT_LIMIT
        limit = max(1, min(limit, _MAX_LIMIT))

        # Goster: sorgu yok
        if not query or not isinstance(query, str) or not query.strip():
            return _son_sessionlar(conn, limit)

        # Ara: sorgu var
        sort_norm = None
        if isinstance(sort, str) and sort.strip().lower() in ("newest", "oldest"):
            sort_norm = sort.strip().lower()

        return _ara(conn, query.strip(), limit, sort_norm)

    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Kontrol fonksiyonu
# ---------------------------------------------------------------------------
def check_session_search_requirements() -> bool:
    """DB dosyasi var mi kontrol et."""
    return _DB_PATH.exists()


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
SESSION_SEARCH_SCHEMA = {
    "name": "session_search",
    "description": (
        "Gecmis konusmalarda FTS5 ile arama yapar. "
        "DORT KULLANIM SEKLI:\n"
        "1) Arama: query='kelime' -> FTS5 ile tara, eslesen session'lari dondurur\n"
        "2) Kaydir: session_id='...', around_message_id=12345 -> mesaj etrafinda pencere\n"
        "3) Oku: session_id='...' -> session'un tamamini doker\n"
        "4) Goster: parametresiz -> en son session'lari listeler\n\n"
        "FTS5 icin AND varsayilan, OR ile genisletebilirsin, "
        "\"tırnak icinde\" tam eslesme, - ile dislama, * ile joker."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Arama sorgusu. FTS5 ile taranir. Bos birakilirsa son session'lari listeler.",
            },
            "limit": {
                "type": "integer",
                "description": "Maksimum sonuc sayisi (varsayilan: 3, maks: 10).",
                "default": 3,
            },
            "session_id": {
                "type": "string",
                "description": "Session ID. around_message_id ile birlikte kullanilirsa kaydirma, tek basina kullanilirsa okuma modu.",
            },
            "around_message_id": {
                "type": "integer",
                "description": "Mesaj ID'si (rowid). session_id ile birlikte kullanilir, o mesaj etrafinda pencere acar.",
            },
            "window": {
                "type": "integer",
                "description": "Kaydirma modunda pencerenin her iki tarafindaki mesaj sayisi (varsayilan: 5, maks: 20).",
                "default": 5,
            },
            "sort": {
                "type": "string",
                "enum": ["newest", "oldest"],
                "description": "Arama modunda siralam: newest (en yeni), oldest (en eski).",
            },
        },
        "required": [],
    },
}


# ---------------------------------------------------------------------------
# Registry kaydi
# ---------------------------------------------------------------------------
from src.reymen.sistem.tools_registry import registry

registry.register(
    name="session_search",
    toolset="session_search",
    schema=SESSION_SEARCH_SCHEMA,
    handler=lambda args, **kw: session_search(
        query=args.get("query") or "",
        limit=args.get("limit", _DEFAULT_LIMIT),
        session_id=args.get("session_id"),
        around_message_id=args.get("around_message_id"),
        window=args.get("window", _DEFAULT_WINDOW),
        sort=args.get("sort"),
    ),
    check_fn=check_session_search_requirements,
    emoji="🔍",
)
