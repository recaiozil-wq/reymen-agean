# -*- coding: utf-8 -*-
"""Schema Manager - SQLite tablo yonetimi + versiyonlama.

Tum SQLite tablolarinin CREATE TABLE IF NOT EXISTS ile idempotent
olusturulmasini saglar. Schema degisikliklerini schema_version
tablosunda takip eder ve migration'lari otomatik calistirir.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Migration Tanimi
# ---------------------------------------------------------------------------


@dataclass
class Migration:
    """Tek bir schema migration'i."""
    version: int
    ad: str
    sql: str = ""
    fn: Optional[Callable[[sqlite3.Connection], None]] = None

    def uygula(self, con: sqlite3.Connection) -> str:
        if self.sql:
            con.executescript(self.sql)
            return self.sql[:80]
        elif self.fn:
            self.fn(con)
            return f"callable:{self.ad}"
        return ""


# ---------------------------------------------------------------------------
# Tablo Tanimi (idempotent CREATE)
# ---------------------------------------------------------------------------


def upsert(sql: str) -> str:
    """CREATE TABLE IF NOT EXISTS ile idempotent tablo olusturma.

    SQL icinde CREATE TABLE varsa otomatik IF NOT EXISTS ekler.
    Yoksa oldugu gibi kullanir (index, trigger vb.).
    """
    if sql.strip().upper().startswith("CREATE TABLE") and "IF NOT EXISTS" not in sql:
        sql = sql.replace("CREATE TABLE", "CREATE TABLE IF NOT EXISTS", 1)
    return sql


# ---------------------------------------------------------------------------
# Schema Manager
# ---------------------------------------------------------------------------


class SchemaManager:
    """SQLite schema yoneticisi - tablo olusturma + versiyonlama.

    Her DB dosyasi icin schema_version tablosu tutar.
    Yeni migration'lar otomatik algilanir ve sirayla calistirilir.
    """

    def __init__(self):
        self._kayitli_dblar: dict[str, int] = {}

    # -- Ana API ------------------------------------------------------------

    def kaydet(self, db_yol: str | Path,
               tablolar: list[str],
               version: int = 1,
               migrations: list[Migration] | None = None) -> dict:
        """Bir DB dosyasinin schema'sini kaydet/guncelle.

        Args:
            db_yol: SQLite dosya yolu.
            tablolar: Idempotent CREATE TABLE SQL listesi.
            version: Schema versiyonu (arttirilinca migration calisir).
            migrations: Migration listesi (versiyon sirali).

        Returns:
            {"durum": "...", "version": N, "degisiklik": [...]}
        """
        yol = Path(db_yol)
        yeni = not yol.exists()
        yol.parent.mkdir(parents=True, exist_ok=True)

        con = sqlite3.connect(str(yol))
        try:
            con.execute("PRAGMA journal_mode=WAL")
            con.execute("PRAGMA synchronous=NORMAL")

            # Schema version tablosu
            con.executescript("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    ad      TEXT PRIMARY KEY,
                    version INTEGER NOT NULL DEFAULT 1,
                    applied_at REAL NOT NULL,
                    metadata TEXT DEFAULT '{}'
                )
            """)

            # Mevcut versiyon
            cur = con.execute(
                "SELECT version FROM schema_version WHERE ad=?",
                ("main",)
            )
            row = cur.fetchone()
            mevcut_ver = row[0] if row else 0

            if mevcut_ver < version:
                uygulanan = []
                if migrations:
                    for m in sorted(migrations, key=lambda x: x.version):
                        if m.version > mevcut_ver and m.version <= version:
                            deg = m.uygula(con)
                            uygulanan.append(f"v{m.version}:{m.ad}({deg})")
                            logger.info("[Schema] %s -> v%d: %s (%s)",
                                       yol.name, m.version, m.ad, deg)

                # Tablolari olustur
                for sql in tablolar:
                    if sql.strip():
                        con.executescript(sql)

                # Versiyonu kaydet
                if mevcut_ver == 0:
                    con.execute(
                        "INSERT INTO schema_version (ad, version, applied_at) VALUES (?, ?, ?)",
                        ("main", version, time.time())
                    )
                else:
                    con.execute(
                        "UPDATE schema_version SET version=?, applied_at=? WHERE ad=?",
                        (version, time.time(), "main")
                    )

                con.commit()
                durum = "olusturuldu" if mevcut_ver == 0 else "guncellendi"
                self._kayitli_dblar[str(yol)] = version
                logger.info("[Schema] %s: v%d -> v%d (%s)",
                           yol.name, mevcut_ver, version, durum)
                return {
                    "durum": durum,
                    "version": version,
                    "onceki": mevcut_ver,
                    "degisiklik": uygulanan,
                }

            self._kayitli_dblar[str(yol)] = mevcut_ver
            return {"durum": "guncel", "version": mevcut_ver}

        except Exception as e:
            logger.error("[Schema] %s hatasi: %s", yol.name, e)
            return {"durum": "hata", "hata": str(e)}
        finally:
            con.close()

    # -- Durum --------------------------------------------------------------

    def durum(self, db_yol: str | Path) -> dict | None:
        """Bir DB'nin schema durumunu goster."""
        yol = Path(db_yol)
        if not yol.exists():
            return None
        try:
            con = sqlite3.connect(str(yol))
            cur = con.execute(
                "SELECT version, applied_at, metadata FROM schema_version WHERE ad=?",
                ("main",)
            )
            row = cur.fetchone()
            con.close()
            if row:
                return {
                    "db": yol.name,
                    "version": row[0],
                    "applied_at": row[1],
                    "metadata": json.loads(row[2]) if row[2] != '{}' else {},
                }
            return {"db": yol.name, "version": 0, "applied_at": 0}
        except Exception as e:
            return {"db": yol.name, "hata": str(e)}

    def tum_durum(self) -> list[dict]:
        """Kayitli tum DB'lerin durumu."""
        return [
            {"yol": yol, "version": ver}
            for yol, ver in self._kayitli_dblar.items()
        ]


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_SCHEMA_MANAGER: SchemaManager | None = None


def schema_manager() -> SchemaManager:
    """Global SchemaManager singleton."""
    global _SCHEMA_MANAGER
    if _SCHEMA_MANAGER is None:
        _SCHEMA_MANAGER = SchemaManager()
    return _SCHEMA_MANAGER


# ---------------------------------------------------------------------------
# Yardimci: Mevcut tablolari tara
# ---------------------------------------------------------------------------


def tablolari_listele(db_yol: str | Path) -> list[str]:
    """Bir DB'deki tum tablolari listele (schema_version dahil)."""
    yol = Path(db_yol)
    if not yol.exists():
        return []
    con = sqlite3.connect(str(yol))
    cur = con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tablolar = [r[0] for r in cur.fetchall()]
    con.close()
    return tablolar


def db_boyut(db_yol: str | Path) -> str:
    """DB dosya boyutunu okunabilir formatta dondur."""
    yol = Path(db_yol)
    if not yol.exists():
        return "0 B"
    boyut = yol.stat().st_size
    for birim in ["B", "KB", "MB", "GB"]:
        if boyut < 1024:
            return f"{boyut:.1f} {birim}"
        boyut /= 1024
    return f"{boyut:.1f} TB"


# ---------------------------------------------------------------------------
# Motor Entegrasyonu
# ---------------------------------------------------------------------------


def motor_kaydet(motor) -> None:
    """Motor'a Schema Manager araclarini kaydet."""
    motor._plugin_arac_kaydet(
        "SCHEMA_DURUM", _schema_durum,
        "SQLite schema versiyonlarini goster. Tum kayitli DB'lerin durumu."
    )
    motor._plugin_arac_kaydet(
        "SCHEMA_TABLOLAR", _schema_tablolar,
        "Bir DB'deki tablolari listele. Kullanim: SCHEMA_TABLOLAR <db_yolu>"
    )
    motor._plugin_arac_kaydet(
        "SCHEMA_TARA", _schema_tara,
        "Projedeki tum SQLite DB'leri tara ve schema durumlarini goster."
    )
    logger.info("[SCHEMA] Motor'a 3 arac kaydedildi")


def _schema_durum(**kw) -> str:
    """Schema durumu."""
    sm = schema_manager()
    durumlar = sm.tum_durum()
    if not durumlar:
        return "  SCHEMA: Kayitli DB yok"
    satirlar = [f"  SCHEMA: {len(durumlar)} DB kayitli"]
    for d in durumlar:
        satirlar.append(f"    - {Path(d['yol']).name}: v{d['version']}")
    return "\n".join(satirlar)


def _schema_tablolar(**kw) -> str:
    args = kw.get("args", [])
    if not args:
        return "[SCHEMA] Kullanim: SCHEMA_TABLOLAR <db_yolu>"
    db = args[0]
    tablolar = tablolari_listele(db)
    if not tablolar:
        return f"[SCHEMA] DB bulunamadi veya tablo yok: {db}"
    return (f"[SCHEMA] {Path(db).name}: {len(tablolari_listele(db))} tablo\n"
            + "\n".join(f"    - {t}" for t in tablolari_listele(db)))


def _schema_tara(**kw) -> str:
    """Projedeki tum SQLite DB'leri tara."""
    import glob
    satirlar = ["[SCHEMA] Proje DB taramasi:"]
    for db in glob.glob("**/*.db", recursive=True):
        if ("__pycache__" in db or "node_modules" in db
                or ".venv" in db):
            continue
        durum = schema_manager().durum(db)
        if durum:
            ver = durum.get("version", "?")
            satirlar.append(f"  {db}: v{ver} ({db_boyut(db)})")
        else:
            satirlar.append(f"  {db}: schema_version yok ({db_boyut(db)})")
    return "\n".join(satirlar)
