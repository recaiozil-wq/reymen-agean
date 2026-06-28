# -*- coding: utf-8 -*-
"""memory_providers/sqlite_provider.py — SQLite + FTS5 bellek."""

from __future__ import annotations
import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BellekSaglayici
import logging
logger = logging.getLogger(__name__)

_DDL = """
CREATE TABLE IF NOT EXISTS bellek (
    namespace TEXT NOT NULL,
    anahtar   TEXT NOT NULL,
    deger     TEXT NOT NULL,
    PRIMARY KEY (namespace, anahtar)
);
CREATE VIRTUAL TABLE IF NOT EXISTS bellek_fts
    USING fts5(anahtar, deger, content='bellek',
               content_rowid='rowid');
CREATE TRIGGER IF NOT EXISTS bellek_ai
    AFTER INSERT ON bellek BEGIN
        INSERT INTO bellek_fts(rowid, anahtar, deger)
        VALUES (new.rowid, new.anahtar, new.deger);
    END;
CREATE TRIGGER IF NOT EXISTS bellek_ad
    AFTER DELETE ON bellek BEGIN
        INSERT INTO bellek_fts(bellek_fts, rowid, anahtar, deger)
        VALUES ('delete', old.rowid, old.anahtar, old.deger);
    END;
CREATE TRIGGER IF NOT EXISTS bellek_au
    AFTER UPDATE ON bellek BEGIN
        INSERT INTO bellek_fts(bellek_fts, rowid, anahtar, deger)
        VALUES ('delete', old.rowid, old.anahtar, old.deger);
        INSERT INTO bellek_fts(rowid, anahtar, deger)
        VALUES (new.rowid, new.anahtar, new.deger);
    END;
"""


class SQLiteBellek(BellekSaglayici):
    """SQLite + FTS5 ile hızlı tam-metin arama belleği."""

    def __init__(self, dosya: str = ".ReYMeN/memories/bellek.db"):
        self._dosya = Path(dosya).resolve()
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._baglanti: Optional[sqlite3.Connection] = None
        self._aktif = False
        self._hata_msg = ""
        self._init()

    def _init(self) -> None:
        try:
            self._baglanti = sqlite3.connect(
                str(self._dosya),
                check_same_thread=False,
                timeout=10,
            )
            self._baglanti.row_factory = sqlite3.Row
            # FTS5 desteği var mı kontrol et
            cur = self._baglanti.execute("SELECT sqlite_compileoption_get(0)")
            self._fts5 = "FTS5" in str(cur.fetchone())
        except Exception as e:
            self._hata_msg = str(e)
            return

        try:
            # executescript trigger'ları da işler
            self._baglanti.executescript(_DDL)
            self._baglanti.commit()
            self._aktif = True
        except Exception as e:
            self._hata_msg = str(e)

    def _bag(self) -> sqlite3.Connection:
        if self._baglanti is None:
            raise RuntimeError("SQLite bağlantısı kapalı.")
        return self._baglanti

    def _guard(self) -> Optional[str]:
        if not self._aktif:
            return f"[Hata]: SQLite kullanılamıyor — {self._hata_msg}"
        return None

    # ── Interface ─────────────────────────────────────────────
    def kaydet(self, anahtar: str, deger: Any,
               namespace: str = "default") -> str:
        if hata := self._guard():
            return hata
        deger_str = json.dumps(deger, ensure_ascii=False) \
                    if not isinstance(deger, str) else deger
        try:
            self._bag().execute(
                """INSERT INTO bellek (namespace, anahtar, deger)
VALUES (?, ?, ?)
                   ON CONFLICT(namespace, anahtar)
                   DO UPDATE SET deger = excluded.deger""",
                (namespace, anahtar, deger_str),
            )
            self._bag().commit()
        except sqlite3.Error as e:
            return f"[Hata]: SQLite kayıt — {e}"
        return f"[Tamam] SQLite: '{anahtar}' → '{namespace}' kaydedildi."

    def oku(self, anahtar: str,
            namespace: str = "default") -> Optional[Any]:
        if self._guard():
            return None
        try:
            satir = self._bag().execute(
                "SELECT deger FROM bellek WHERE namespace=? AND anahtar=?",
                (namespace, anahtar),
            ).fetchone()
            if satir:
                try:
                    return json.loads(satir["deger"])
                except (json.JSONDecodeError, TypeError):
                    return satir["deger"]
        except sqlite3.Error:
            logger.warning("[fix_01_sessiz_except] Error")
        return None

    def ara(self, sorgu: str, limit: int = 5) -> List[Dict]:
        if self._guard():
            return []
        if not sorgu.strip():
            return []
        try:
            if self._fts5:
                satirlar = self._bag().execute(
                    """SELECT b.namespace, b.anahtar, b.deger
                       FROM bellek_fts f
                       JOIN bellek b ON b.rowid = f.rowid
                       WHERE bellek_fts MATCH ?
                       LIMIT ?""",
                    (sorgu, limit),
                ).fetchall()
            else:
                # FTS5 yok → LIKE fallback
                pat = f"%{sorgu}%"
                satirlar = self._bag().execute(
                    """SELECT namespace, anahtar, deger FROM bellek
                       WHERE anahtar LIKE ? OR deger LIKE ?
                       LIMIT ?""",
                    (pat, pat, limit),
                ).fetchall()
        except sqlite3.Error:
            return []
        return [
            {
                "id":     f"{r['namespace']}:{r['anahtar']}",
                "icerik": self._sinirla(r["deger"]),
            }
            for r in satirlar
        ]

    def sil(self, anahtar: str, namespace: str = "default") -> str:
        if hata := self._guard():
            return hata
        try:
            cur = self._bag().execute(
                "DELETE FROM bellek WHERE namespace=? AND anahtar=?",
                (namespace, anahtar),
            )
            self._bag().commit()
        except sqlite3.Error as e:
            return f"[Hata]: SQLite silme — {e}"
        if cur.rowcount == 0:
            return f"[Hata]: '{anahtar}' → '{namespace}' bulunamadı."
        return f"[Tamam] SQLite: '{anahtar}' silindi."

    def durum(self) -> Dict:
        if not self._aktif:
            return {"tur": "sqlite", "aktif": False, "hata": self._hata_msg}
        try:
            sayi = self._bag().execute(
                "SELECT COUNT(*) FROM bellek"
            ).fetchone()[0]
            ns_sayi = self._bag().execute(
                "SELECT COUNT(DISTINCT namespace) FROM bellek"
            ).fetchone()[0]
        except sqlite3.Error:
            sayi = ns_sayi = -1
        return {
            "tur":       "sqlite",
            "aktif":     True,
            "fts5":      self._fts5,
            "kayit":     sayi,
            "namespace": ns_sayi,
            "dosya":     str(self._dosya),
        }

    def __del__(self) -> None:
        """GC sırasında bağlantıyı kapat."""
        try:
            if self._baglanti:
                self._baglanti.close()
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
