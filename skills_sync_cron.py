#!/usr/bin/env python3
"""
skills_sync_cron.py — Cron job: scan .md files in skills/ and sync to OnceHafiza DB.
Run every 6 hours. Reports new vs updated count.
"""

import hashlib
import logging
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("skills_sync")

# ── Paths ──────────────────────────────────────────────────────────────
ROOT = Path("C:/Users/marko/Desktop/Reymen Proje/ReYMeN-Ajan")
SKILLS_DIR = ROOT / "skills"
DB_PATH = ROOT / "merkez_db" / "skills_index.db"


def md_parse_meta(filepath: str, content: str) -> tuple[str, str]:
    """
    Extract description and category from markdown frontmatter.
    Returns (aciklama, kategori).
    """
    aciklama = ""
    kategori = ""

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            for line in frontmatter.strip().split("\n"):
                line = line.strip()
                if line.startswith("description:"):
                    aciklama = line[len("description:"):].strip().strip('"').strip("'")
                elif line.startswith("name:"):
                    if not aciklama:
                        aciklama = line[len("name:"):].strip().strip('"').strip("'")
                elif line.startswith("category:"):
                    kategori = line[len("category:"):].strip().strip('"').strip("'")
                elif line.startswith("tags:"):
                    kategori = kategori or line[len("tags:"):].strip().strip('"').strip("'")

    # Fallback: use first non-empty line
    if not aciklama:
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("---") and not line.startswith("#"):
                aciklama = line[:100]
                break
            if line.startswith("#"):
                aciklama = line.lstrip("#").strip()[:100]
                break

    if not kategori:
        fname = Path(filepath).stem
        if fname.startswith("skill-"):
            kategori = "skill"
        elif fname.startswith("prompt-"):
            kategori = "prompt"
        elif fname.startswith("ReYMeN-"):
            kategori = "reymen"
        else:
            kategori = "genel"

    return aciklama[:200], kategori[:50]


def file_hash(filepath: str) -> str:
    """SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def update_skill_in_db(
    con: sqlite3.Connection,
    ad: str,
    icerik: str,
    aciklama: str,
    kaynak: str,
    kategori: str,
    dosya_hash: str,
) -> None:
    """Insert or update a skill record in beceriler + beceriler_meta."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # Upsert beceriler
    con.execute(
        """INSERT INTO beceriler (ad, aciklama, icerik, kaynak)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(ad) DO UPDATE SET
               aciklama = excluded.aciklama,
               icerik = excluded.icerik,
               kaynak = excluded.kaynak""",
        (ad, aciklama, icerik, kaynak),
    )

    # Upsert beceriler_meta
    con.execute(
        """INSERT INTO beceriler_meta (ad, dosya_hash, guncelleme)
           VALUES (?, ?, ?)
           ON CONFLICT(ad) DO UPDATE SET
               dosya_hash = excluded.dosya_hash,
               guncelleme = excluded.guncelleme""",
        (ad, dosya_hash, now),
    )


def main() -> tuple[int, int, int]:
    """
    Sync skills/ .md files to skills_index.db.
    Returns (new_count, updated_count, removed_count).
    """
    if not SKILLS_DIR.is_dir():
        logger.error("Skills directory not found: %s", SKILLS_DIR)
        return 0, 0, 0

    os.makedirs(DB_PATH.parent, exist_ok=True)

    # Load existing hashes from DB
    con = sqlite3.connect(str(DB_PATH), timeout=15)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")

    # Ensure tables exist
    con.executescript("""
        CREATE TABLE IF NOT EXISTS beceriler (
            ad        TEXT PRIMARY KEY,
            aciklama  TEXT DEFAULT '',
            icerik    TEXT DEFAULT '',
            kaynak    TEXT DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS beceriler_meta (
            ad            TEXT PRIMARY KEY,
            dosya_hash    TEXT DEFAULT '',
            guncelleme    TEXT DEFAULT (datetime('now'))
        );
    """)
    con.commit()

    existing = {}
    try:
        rows = con.execute(
            "SELECT ad, dosya_hash FROM beceriler_meta"
        ).fetchall()
        existing = {row[0]: row[1] for row in rows}
    except Exception:
        pass

    # Scan .md files
    md_files = sorted(SKILLS_DIR.glob("*.md"))
    new_count = 0
    updated_count = 0

    for fp in md_files:
        ad = fp.name
        current_hash = file_hash(str(fp))
        old_hash = existing.get(ad)

        if old_hash is None:
            action = "NEW"
            new_count += 1
        elif old_hash != current_hash:
            action = "UPD"
            updated_count += 1
        else:
            continue

        content = fp.read_text(encoding="utf-8", errors="replace")
        aciklama, kategori = md_parse_meta(str(fp), content)
        kaynak = str(fp.resolve())

        update_skill_in_db(con, ad, content, aciklama, kaynak, kategori, current_hash)
        con.commit()
        logger.info("[%s] %s (%d chars, hash=%s)", action, ad, len(content), current_hash[:12])

    # Remove rows for files that no longer exist on disk
    all_file_names = {fp.name for fp in md_files}
    orphans = [ad for ad in existing if ad not in all_file_names]
    for ad in orphans:
        con.execute("DELETE FROM beceriler WHERE ad = ?", (ad,))
        con.execute("DELETE FROM beceriler_meta WHERE ad = ?", (ad,))
        logger.info("[DEL] %s (file removed)", ad)
    con.commit()
    con.close()

    logger.info(
        "Sync complete: %d new, %d updated, %d removed (total: %d)",
        new_count, updated_count, len(orphans), len(md_files)
    )
    return new_count, updated_count, len(orphans)


if __name__ == "__main__":
    new, upd, rem = main()
    print(f"RESULT|new={new}|updated={upd}|removed={rem}")
