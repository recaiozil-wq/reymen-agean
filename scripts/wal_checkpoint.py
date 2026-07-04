# -*- coding: utf-8 -*-
"""
wal_checkpoint.py — TUM SQLite DB'lerde WAL checkpoint atar.

Her 6 saatte bir calisir (cron ile). Tum .db dosyalarini tarar,
WAL modundakilere TRUNCATE checkpoint uygular.
"""

import os
import sqlite3
import sys
from pathlib import Path

_PROJE_KOK = Path(__file__).resolve().parent.parent

def _bul_db_dosyalari():
    """Proje altindaki tum .db dosyalarini bul (node_modules, .venv, .git haric)."""
    dbs = []
    for root, dirs, files in os.walk(_PROJE_KOK):
        # Gereksiz klasorleri atla
        skip_dirs = {"node_modules", ".venv", "venv", ".git", "__pycache__", 
                     ".hermes", "terminal-bench-benchmark", "apps"}
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for f in files:
            if f.endswith(".db") or f.endswith(".db-wal"):
                dbs.append(Path(root) / f)
    return dbs

def _checkpoint_uygula(db_yolu):
    """Bir DB dosyasina WAL checkpoint uygula."""
    gercek_db = str(db_yolu).replace("-wal", "") if str(db_yolu).endswith("-wal") else str(db_yolu)
    if not os.path.exists(gercek_db):
        return "ATLANDI (gercek dosya yok)"
    try:
        conn = sqlite3.connect(gercek_db, timeout=5)
        cur = conn.cursor()
        # WAL modunda mi kontrol et
        cur.execute("PRAGMA journal_mode")
        jm = cur.fetchone()[0]
        if jm != "wal" and jm != "WAL":
            conn.close()
            return f"ATLANDI (journal={jm})"
        # Checkpoint uygula
        cur.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        sonuc = cur.fetchone()
        conn.close()
        return f"CHECKPOINT: {sonuc}"
    except Exception as e:
        return f"HATA: {e}"

def main():
    dbs = _bul_db_dosyalari()
    print(f"Taranan DB dosyasi: {len(dbs)}")
    basarili = 0
    basarisiz = 0
    for db in sorted(dbs):
        sonuc = _checkpoint_uygula(db)
        if "CHECKPOINT" in sonuc:
            basarili += 1
        elif "ATLANDI" in sonuc:
            pass
        else:
            basarisiz += 1
            print(f"  {db.name}: {sonuc}")
    print(f"Checkpoint: {basarili} basarili, {basarisiz} hata")
    return 0 if basarisiz == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
