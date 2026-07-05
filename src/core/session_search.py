# -*- coding: utf-8 -*-
"""
reymen/core/session_search.py â€” Session Full-Text Search (FTS5).

session.db iÃ§indeki session_messages tablosunda FTS5 ile hÄ±zlÄ± arama yapar.
Mevcut FTS5 tablolarÄ± (session_messages_fts, session_messages_trigram) kullanÄ±lÄ±r.

KullanÄ±m:
    from reymen.core.session_search import session_ara
    sonuclar = session_ara("hata dÃ¼zeltme", limit=10)
"""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Session DB yolu
DB_PATH = Path(__file__).parent.parent.parent / "reymen" / "merkez_db" / "session.db"


@contextmanager
def _db():
    """SQLite baÄŸlam yÃ¶neticisi."""
    con = sqlite3.connect(str(DB_PATH), timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA busy_timeout=5000")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _fts5_mevcut_mu() -> bool:
    """FTS5 tablolarÄ± mevcut mu kontrol et."""
    try:
        with _db() as con:
            cursor = con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='session_messages_fts'"
            )
            return cursor.fetchone() is not None
    except Exception:
        return False


def session_ara(
    sorgu: str,
    limit: int = 10,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Session mesajlarÄ±nda FTS5 ile full-text arama yap.

    Args:
        sorgu: Arama sorgusu (FTS5 syntax destekler)
        limit: Maksimum sonuÃ§ sayÄ±sÄ±
        session_id: Belirli bir session ile sÄ±nÄ±rla (None = tÃ¼m sessionlar)

    Returns:
        SonuÃ§ listesi: [{"session_id": ..., "rol": ..., "icerik": ..., "skor": ..., "created_at": ...}]
    """
    if not sorgu.strip():
        return []

    # FTS5 sorgusunu gÃ¼venli hale getir
    # Ã–zel karakterleri escape et, sadece kelime arama
    guvenli_sorgu = _fts5_sorgu_hazirla(sorgu)

    try:
        with _db() as con:
            if session_id:
                # Belirli session'da ara
                cursor = con.execute(
                    """
                    SELECT m.session_id, m.rol, m.icerik, m.created_at,
                           bm25(session_messages_fts) as skor
                    FROM session_messages_fts
                    JOIN session_messages m ON m.id = session_messages_fts.rowid
                    WHERE session_messages_fts MATCH ?
                      AND m.session_id = ?
                    ORDER BY skor
                    LIMIT ?
                    """,
                    (guvenli_sorgu, session_id, limit),
                )
            else:
                # TÃ¼m sessionlarda ara
                cursor = con.execute(
                    """
                    SELECT m.session_id, m.rol, m.icerik, m.created_at,
                           bm25(session_messages_fts) as skor
                    FROM session_messages_fts
                    JOIN session_messages m ON m.id = session_messages_fts.rowid
                    WHERE session_messages_fts MATCH ?
                    ORDER BY skor
                    LIMIT ?
                    """,
                    (guvenli_sorgu, limit),
                )

            sonuclar = []
            for row in cursor.fetchall():
                sonuclar.append(
                    {
                        "session_id": row["session_id"],
                        "rol": row["rol"],
                        "icerik": row["icerik"][:500],  # Ä°lk 500 karakter
                        "skor": round(row["skor"], 4) if row["skor"] else 0,
                        "created_at": row["created_at"],
                    }
                )

            return sonuclar

    except sqlite3.OperationalError as e:
        logger.warning("FTS5 arama hatasÄ±: %s â€” trigram fallback denenecek", e)
        return _trigram_ara(sorgu, limit, session_id)
    except Exception as e:
        logger.error("Session arama hatasÄ±: %s", e)
        return []


def _trigram_ara(
    sorgu: str,
    limit: int = 10,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Trigram FTS ile fallback arama (LIKE yerine)."""
    try:
        with _db() as con:
            if session_id:
                cursor = con.execute(
                    """
                    SELECT m.session_id, m.rol, m.icerik, m.created_at
                    FROM session_messages m
                    WHERE m.icerik LIKE ? AND m.session_id = ?
                    ORDER BY m.created_at DESC
                    LIMIT ?
                    """,
                    (f"%{sorgu}%", session_id, limit),
                )
            else:
                cursor = con.execute(
                    """
                    SELECT m.session_id, m.rol, m.icerik, m.created_at
                    FROM session_messages m
                    WHERE m.icerik LIKE ?
                    ORDER BY m.created_at DESC
                    LIMIT ?
                    """,
                    (f"%{sorgu}%", limit),
                )

            sonuclar = []
            for row in cursor.fetchall():
                sonuclar.append(
                    {
                        "session_id": row["session_id"],
                        "rol": row["rol"],
                        "icerik": row["icerik"][:500],
                        "skor": 0,
                        "created_at": row["created_at"],
                    }
                )
            return sonuclar
    except Exception as e:
        logger.error("Trigram arama hatasÄ±: %s", e)
        return []


def _fts5_sorgu_hazirla(sorgu: str) -> str:
    """FTS5 sorgusunu gÃ¼venli hale getir.

    FTS5 Ã¶zel karakterleri: " * ( ) OR AND NOT NEAR
    Kelimeleri tÄ±rnak iÃ§ine alarak tam eÅŸleÅŸme arar.
    """
    # Ã–zel karakterleri temizle
    temiz = sorgu.replace('"', "").replace("*", "").replace("(", "").replace(")", "")

    # Kelimeleri ayÄ±r
    kelimeler = temiz.split()

    if not kelimeler:
        return sorgu

    # Her kelimeyi Ã¶nek arama (*) ile sarmala
    # FTS5: "kelime1" "kelime2" â†’ AND mantÄ±ÄŸÄ±
    fts_sorgu = " ".join(f'"{k}"*' for k in kelimeler)
    return fts_sorgu


def session_listele(limit: int = 20) -> List[Dict[str, Any]]:
    """TÃ¼m session'larÄ± listele.

    Args:
        limit: Maksimum session sayÄ±sÄ±

    Returns:
        Session listesi: [{"id": ..., "source": ..., "started_at": ..., "message_count": ...}]
    """
    try:
        with _db() as con:
            cursor = con.execute(
                """
                SELECT id, source, user_id, model, started_at, ended_at,
                       message_count, tool_call_count, title
                FROM sessions
                ORDER BY started_at DESC
                LIMIT ?
                """,
                (limit,),
            )

            sonuclar = []
            for row in cursor.fetchall():
                sonuclar.append(
                    {
                        "id": row["id"],
                        "source": row["source"],
                        "user_id": row["user_id"],
                        "model": row["model"],
                        "started_at": row["started_at"],
                        "ended_at": row["ended_at"],
                        "message_count": row["message_count"],
                        "tool_call_count": row["tool_call_count"],
                        "title": row["title"],
                    }
                )
            return sonuclar
    except Exception as e:
        logger.error("Session listeleme hatasÄ±: %s", e)
        return []


def session_mesajlari(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Bir session'Ä±n mesajlarÄ±nÄ± getir.

    Args:
        session_id: Session ID
        limit: Maksimum mesaj sayÄ±sÄ±

    Returns:
        Mesaj listesi
    """
    try:
        with _db() as con:
            cursor = con.execute(
                """
                SELECT id, session_id, rol, icerik, created_at
                FROM session_messages
                WHERE session_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (session_id, limit),
            )

            sonuclar = []
            for row in cursor.fetchall():
                sonuclar.append(
                    {
                        "id": row["id"],
                        "session_id": row["session_id"],
                        "rol": row["rol"],
                        "icerik": row["icerik"],
                        "created_at": row["created_at"],
                    }
                )
            return sonuclar
    except Exception as e:
        logger.error("Session mesaj getirme hatasÄ±: %s", e)
        return []


def session_istatistik() -> Dict[str, Any]:
    """Session DB istatistikleri."""
    try:
        with _db() as con:
            session_sayisi = con.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
            mesaj_sayisi = con.execute(
                "SELECT COUNT(*) FROM session_messages"
            ).fetchone()[0]
            tool_cagri_sayisi = con.execute(
                "SELECT COUNT(*) FROM session_tool_calls"
            ).fetchone()[0]

            # FTS5 tablo var mÄ±
            fts_var = _fts5_mevcut_mu()

            return {
                "session_sayisi": session_sayisi,
                "mesaj_sayisi": mesaj_sayisi,
                "tool_cagri_sayisi": tool_cagri_sayisi,
                "fts5_aktif": fts_var,
                "db_yolu": str(DB_PATH),
            }
    except Exception as e:
        logger.error("Session istatistik hatasÄ±: %s", e)
        return {"hata": str(e)}


# â”€â”€ CLI â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("KullanÄ±m: python -m reymen.core.session_search <sorgu> [--limit N]")
        print("          python -m reymen.core.session_search --list")
        print("          python -m reymen.core.session_search --stats")
        sys.exit(1)

    if sys.argv[1] == "--list":
        for s in session_listele():
            print(
                f"  [{s['id'][:8]}] {s.get('title', 'BaÅŸlÄ±ksÄ±z')} â€” {s['message_count']} mesaj"
            )
    elif sys.argv[1] == "--stats":
        print(json.dumps(session_istatistik(), indent=2, ensure_ascii=False))
    else:
        sorgu = sys.argv[1]
        limit = 10
        if "--limit" in sys.argv:
            idx = sys.argv.index("--limit")
            if idx + 1 < len(sys.argv):
                limit = int(sys.argv[idx + 1])

        sonuclar = session_ara(sorgu, limit=limit)
        print(f"\n{'='*60}")
        print(f"  Arama: '{sorgu}' â€” {len(sonuclar)} sonuÃ§")
        print(f"{'='*60}\n")
        for i, s in enumerate(sonuclar, 1):
            print(f"  [{i}] Session: {s['session_id'][:8]}...")
            print(f"      Rol: {s['rol']}")
            print(f"      Skor: {s['skor']}")
            print(f"      Ä°Ã§erik: {s['icerik'][:200]}...")
            print()
