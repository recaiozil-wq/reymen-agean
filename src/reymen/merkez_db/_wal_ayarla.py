"""TÃ¼m merkez_db'deki SQLite dosyalarÄ±na WAL + busy_timeout uygula."""

import sqlite3, os
import logging

logger = logging.getLogger(__name__)

DB_DIR = os.path.dirname(os.path.abspath(__file__))
dbs = [f for f in os.listdir(DB_DIR) if f.endswith(".db")]

print("=== DB PERFORMANS AYARLARI ===")
for db in sorted(dbs):
    yol = os.path.join(DB_DIR, db)
    try:
        con = sqlite3.connect(yol, timeout=10)
        cur = con.cursor()

        # Her PRAGMA ayrÄ± ayrÄ±
        cur.execute("PRAGMA journal_mode=WAL")
        jm = cur.fetchone()
        jm = jm[0] if jm else "?"

        cur.execute("PRAGMA busy_timeout=5000")
        bt = cur.fetchone()
        bt = bt[0] if bt else "?"

        cur.execute("PRAGMA synchronous=NORMAL")

        con.close()
        print(f"  âœ… {db:30s} journal={str(jm):4s} busy={bt}ms")
    except Exception as e:
        print(f"  âŒ {db:30s} HATA: {e}")

print("\nâœ… TÃ¼m DB'lere WAL + busy_timeout uygulandÄ±")
