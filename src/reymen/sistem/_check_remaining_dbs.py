#!/usr/bin/env python3
"""Check remaining unclassified DBs"""

import sqlite3, os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

_KOK = Path(__file__).resolve().parent.parent.parent  # ReYMeN-Ajan
DBS = {
    "kanban.db": str(_KOK / ".ReYMeN" / "kanban.db"),
    "memory_fts.db": str(_KOK / ".ReYMeN" / "memory_fts.db"),
    "session.db": str(_KOK / ".ReYMeN" / "session.db"),
    "skill_index.db": str(_KOK / ".ReYMeN" / "skill_index.db"),
    "steering.db": str(_KOK / "reymen" / "cereyan" / ".reymen_hafiza" / "steering.db"),
    "hatalar.db": str(_KOK / "reymen" / "hafiza" / "hatalar.db"),
    "ogrenme.db": str(_KOK / "reymen" / "hafiza" / "ogrenme.db"),
    "state.db": str(
        Path.home()
        / "AppData"
        / "Local"
        / "hermes"
        / "profiles"
        / "reymen"
        / "state.db"
    ),
}

for name, path in DBS.items():
    if not os.path.exists(path):
        print(f"{name:20s} DOSYA YOK")
        continue
    size = os.path.getsize(path)
    try:
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = c.fetchall()
        total_records = 0
        details = []
        for t in tables:
            tn = t[0]
            if tn.startswith("sqlite_"):
                continue
            c2 = conn.cursor()
            c2.execute(f'SELECT COUNT(*) FROM "{tn}"')
            count = c2.fetchone()[0]
            total_records += count
            details.append(f"{tn}({count})")
        detail_str = ", ".join(details[:5])
        if len(details) > 5:
            detail_str += f"... +{len(details)-5}"
        print(f"{name:20s} {size//1024:>7d}KB {total_records:>7d} kayit [{detail_str}]")
        conn.close()
    except Exception as e:
        print(f"{name:20s} {size//1024:>7d}KB HATA: {str(e)[:60]}")

print("\n✅ Taranan DB sayisi:", len(DBS))
