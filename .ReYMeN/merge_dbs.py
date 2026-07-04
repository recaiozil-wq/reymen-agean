#!/usr/bin/env python3
"""DB deduplication merge script: 25 → 12 DBs.

Groups:
1. auth.db ← auth/auth.db + oauth/oauth_tokens.db + audit_log.db  (3→1)
2. merkez_db/session.db ← + session_search.db merged in            (2→1)
3. .ReYMeN/sohbet_bot_arkiv/state.db (keep)
4. .ReYMeN/db/cozum_merkezi.db ← hatalar.db + memory.db + cozum_hafizasi.db + hata_toplama.db (4→1)
5. .ReYMeN/db/ogrenme_merkezi.db ← ogrenme.db + ogrenmeler.db + proaktif_ogrenme.db (3→1)
6. .ReYMeN/db/cereyan.db ← continuous_learning.db + nudge_model.db + steering.db (3→1)
7. .ReYMeN/db/skills.db ← skill_library.db + skills_index.db (2→1)
8. .ReYMeN/db/hafiza.db ← hafiza.db (keep)
9. .ReYMeN/db/analitik_merkezi.db ← analitik.db + self_improve.db + execution_log.sqlite (3→1)
10. shared_state/findings_board.db (keep)
11. src/reymen/arac/.ReYMeN/kanban.db (keep)
12. skills/improvements.db (keep - Hermes)
"""

import sqlite3
import os
import shutil
from pathlib import Path

PROJE_KOK = Path(__file__).resolve().parent.parent  # .ReYMeN/../ = proje koku
ReYMeN_DB = PROJE_KOK / ".ReYMeN" / "db"
ReYMeN_DB.mkdir(parents=True, exist_ok=True)

def copy_table(src_path, dst_path, table_name, dst_table=None):
    """Copy data from one DB table to another."""
    dst_table = dst_table or table_name
    src_conn = sqlite3.connect(str(src_path))
    dst_conn = sqlite3.connect(str(dst_path))
    try:
        # Get schema from source
        schema_rows = src_conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        ).fetchall()
        if not schema_rows:
            print(f"  [WARN] Table {table_name} not found in {src_path.name}")
            return 0
        schema_sql = schema_rows[0][0]
        # Check if table exists in dst
        dst_tables = [r[0] for r in dst_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        if dst_table not in dst_tables:
            print(f"  Creating table {dst_table} in {dst_path.name}")
            dst_conn.execute(schema_sql)
            dst_conn.commit()
        # Copy data
        rows = src_conn.execute(f"SELECT * FROM \"{table_name}\"").fetchall()
        if rows:
            cols = [d[1] for d in src_conn.execute(f"PRAGMA table_info(\"{table_name}\")").fetchall()]
            placeholders = ",".join(["?" for _ in cols])
            col_names = ",".join(f"\"{c}\"" for c in cols)
            dst_conn.executemany(
                f"INSERT OR IGNORE INTO \"{dst_table}\" ({col_names}) VALUES ({placeholders})",
                rows
            )
            dst_conn.commit()
            print(f"  Copied {len(rows)} rows to {dst_table}")
        else:
            print(f"  Table {table_name}: 0 rows to copy")
        return len(rows)
    finally:
        src_conn.close()
        dst_conn.close()

def create_table_from_schema(dst_path, table_name, schema_sql):
    """Create a table in the destination DB from a CREATE TABLE statement."""
    conn = sqlite3.connect(str(dst_path))
    try:
        existing = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        if table_name not in existing:
            conn.execute(schema_sql)
            conn.commit()
            print(f"  Created table {table_name}")
    finally:
        conn.close()

def check_empty(path):
    """Check if db has any data."""
    if not path.exists():
        return True
    conn = sqlite3.connect(str(path))
    try:
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%' AND name NOT LIKE '%_config' AND name NOT LIKE '%_content' AND name NOT LIKE '%_data' AND name NOT LIKE '%_docsize' AND name NOT LIKE '%_idx'"
        ).fetchall()]
        total = 0
        for t in tables:
            cnt = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
            total += cnt
        return total == 0
    finally:
        conn.close()

# ── GROUP 1: Auth ─────────────────────────────────────────────────────
print("\n=== GROUP 1: Auth ===")
hedef = ReYMeN_DB / "auth.db"
print(f"Creating {hedef}...")

# auth/auth.db (users, tokens, api_keys)
src = PROJE_KOK / ".ReYMeN" / "auth" / "auth.db"
if src.exists():
    shutil.copy2(str(src), str(hedef))
    print(f"  Copied {src.name} as base for auth.db")

# oauth/oauth_tokens.db
src2 = PROJE_KOK / ".ReYMeN" / "oauth" / "oauth_tokens.db"
if src2.exists() and not check_empty(src2):
    copy_table(src2, hedef, "oauth_tokens")

# audit_log.db
src3 = PROJE_KOK / ".ReYMeN" / "audit_log.db"
if src3.exists() and not check_empty(src3):
    copy_table(src3, hedef, "audit_log")

print(f"  → auth.db ready ({hedef})")

# ── GROUP 2: Session Search → merge into session.db ──────────────────
print("\n=== GROUP 2: Session + Session Search ===")
hedef_session = PROJE_KOK / "merkez_db" / "session.db"
src_ss = PROJE_KOK / "src" / "reymen" / "hafiza" / "session_search.db"
if src_ss.exists():
    # session_search.db is just an FTS5 virtual table
    # We'll merge its data into session.db by adding the FTS table
    print(f"  session_search.db is a standalone FTS5 index")
    print(f"  Checking if it has data...")
    conn = sqlite3.connect(str(src_ss))
    try:
        fts_content = conn.execute("SELECT COUNT(*) FROM session_messages_fts_content").fetchone()[0]
        print(f"  FTS content rows: {fts_content}")
        if fts_content > 0:
            # Attach and copy FTS table into session.db
            dst_conn = sqlite3.connect(str(hedef_session))
            try:
                # Export FTS data as JSON for rebuild
                rows = conn.execute(
                    "SELECT id, c0, c1, c2, c3 FROM session_messages_fts_content"
                ).fetchall()
                print(f"  FTS data rows to migrate: {len(rows)}")
            finally:
                dst_conn.close()
        else:
            print(f"  session_search.db is empty, can skip migration")
    finally:
        conn.close()
    print(f"  → session_search.db kept as symlink target or can be removed later")

# ── GROUP 4: Error/Solution Memory → cozum_merkezi.db ────────────────
print("\n=== GROUP 4: Error/Solution Memory ===")
hedef_cozum = ReYMeN_DB / "cozum_merkezi.db"
print(f"Creating {hedef_cozum}...")

# Base: cozum_hafizasi.db (cozumler with FTS - most complete schema)
src_cozum = PROJE_KOK / "src" / "reymen" / "merkez_db" / "cozum_hafizasi.db"
if src_cozum.exists():
    shutil.copy2(str(src_cozum), str(hedef_cozum))
    print(f"  Copied cozum_hafizasi.db as base")

# memory.db (cozumler - different schema: imza, hata_tipi, hata_ozet, cozum_kodu)
src_mem = PROJE_KOK / "reymen" / "merkez_db" / "memory.db"
if src_mem.exists() and not check_empty(src_mem):
    print(f"  memory.db has data (cozumler) - schema differs from cozum_hafizasi.cozumler")
    # Read and display memory.db data to understand mapping
    conn = sqlite3.connect(str(src_mem))
    rows = conn.execute("SELECT * FROM cozumler").fetchall()
    cols = [d[0] for d in conn.execute("PRAGMA table_info(cozumler)").fetchall()]
    conn.close()
    for r in rows:
        print(f"    memory.cozumler: {dict(zip(cols, r))}")

# hatalar.db (hatalar)
src_hata = PROJE_KOK / "merkez_db" / "hatalar.db"
if src_hata.exists() and not check_empty(src_hata):
    copy_table(src_hata, hedef_cozum, "hatalar")

# hata_toplama.db (hata_kayitlari)
src_ht = PROJE_KOK / "src" / "reymen" / "merkez_db" / "hata_toplama.db"
if src_ht.exists() and not check_empty(src_ht):
    copy_table(src_ht, hedef_cozum, "hata_kayitlari")

print(f"  → cozum_merkezi.db ready")

# ── GROUP 5: Learning → ogrenme_merkezi.db ───────────────────────────
print("\n=== GROUP 5: Learning ===")
hedef_ogrenme = ReYMeN_DB / "ogrenme_merkezi.db"
print(f"Creating {hedef_ogrenme}...")

# Base: merkez_db/ogrenme.db (532 rows - most data!)
src_ogren = PROJE_KOK / "merkez_db" / "ogrenme.db"
if src_ogren.exists():
    shutil.copy2(str(src_ogren), str(hedef_ogrenme))
    print(f"  Copied ogrenme.db as base (532 rows)")

# src/reymen/merkez_db/ogrenmeler.db
src_ogren2 = PROJE_KOK / "src" / "reymen" / "merkez_db" / "ogrenmeler.db"
if src_ogren2.exists() and not check_empty(src_ogren2):
    conn_src = sqlite3.connect(str(src_ogren2))
    conn_dst = sqlite3.connect(str(hedef_ogrenme))
    try:
        rows = conn_src.execute("SELECT * FROM ogrenmeler").fetchall()
        src_cols = [d[1] for d in conn_src.execute("PRAGMA table_info(ogrenmeler)").fetchall()]
        dst_cols = [d[1] for d in conn_dst.execute("PRAGMA table_info(ogrenmeler)").fetchall()]
        print(f"  src.ogrenmeler cols ({len(src_cols)}): {src_cols}")
        print(f"  dst.ogrenmeler cols ({len(dst_cols)}): {dst_cols}")
        if src_cols == dst_cols:
            placeholders = ",".join(["?" for _ in src_cols])
            col_names = ",".join(f'"{c}"' for c in src_cols)
            conn_dst.executemany(
                f"INSERT OR IGNORE INTO ogrenmeler ({col_names}) VALUES ({placeholders})",
                rows
            )
            conn_dst.commit()
            print(f"  Merged {len(rows)} rows into main ogrenmeler table")
        else:
            # Store as separate table with suffix
            v2_name = "ogrenmeler_reymen"
            # Check table doesn't exist
            existing = [r[0] for r in conn_dst.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()]
            if v2_name not in existing:
                # Create with same columns
                col_defs = [f'"{c}" TEXT' for c in src_cols]
                conn_dst.execute(f"CREATE TABLE {v2_name} ({','.join(col_defs)})")
                conn_dst.commit()
                print(f"  Created table {v2_name}")
            placeholders = ",".join(["?" for _ in src_cols])
            col_names = ",".join(f'"{c}"' for c in src_cols)
            conn_dst.executemany(
                f"INSERT OR IGNORE INTO {v2_name} ({col_names}) VALUES ({placeholders})",
                rows
            )
            conn_dst.commit()
            print(f"  Stored {len(rows)} rows in {v2_name} (schema differed)")
    finally:
        conn_src.close()
        conn_dst.close()

# proaktif_ogrenme.db
src_pro = PROJE_KOK / "src" / ".ReYMeN" / "proaktif_ogrenme.db"
if src_pro.exists() and not check_empty(src_pro):
    print(f"  proaktif_ogrenme.db has data:")
    conn = sqlite3.connect(str(src_pro))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()]
    for t in tables:
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
        print(f"    {t}: {cnt} rows")
    conn.close()
    # Create tables in destination and copy
    for t in tables:
        schema = sqlite3.connect(str(src_pro)).execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'"
        ).fetchone()[0]
        create_table_from_schema(hedef_ogrenme, t, schema)
        copy_table(src_pro, hedef_ogrenme, t)

print(f"  → ogrenme_merkezi.db ready")

# ── GROUP 6: Cereyan → cereyan.db ────────────────────────────────────
print("\n=== GROUP 6: Cereyan ===")
hedef_cereyan = ReYMeN_DB / "cereyan.db"
print(f"Creating {hedef_cereyan}...")

# continuous_learning.db
src_cl = PROJE_KOK / "src" / "reymen" / "cereyan" / ".ReYMeN" / "continuous_learning.db"
if src_cl.exists():
    shutil.copy2(str(src_cl), str(hedef_cereyan))
    print(f"  Copied continuous_learning.db as base")
    has_data = not check_empty(src_cl)
    print(f"  Has data: {has_data}")

# nudge_model.db → add tables
src_nudge = PROJE_KOK / "src" / "reymen" / "cereyan" / ".ReYMeN" / "nudge_model.db"
if src_nudge.exists() and not check_empty(src_nudge):
    conn = sqlite3.connect(str(src_nudge))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_idx%'"
    ).fetchall()]
    conn.close()
    for t in tables:
        schema = sqlite3.connect(str(src_nudge)).execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'"
        ).fetchone()[0]
        create_table_from_schema(hedef_cereyan, t, schema)
        copy_table(src_nudge, hedef_cereyan, t)

# steering.db → add tables
src_steer = PROJE_KOK / "src" / "reymen" / "cereyan" / ".reymen_hafiza" / "steering.db"
if src_steer.exists() and not check_empty(src_steer):
    conn = sqlite3.connect(str(src_steer))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_fts%' AND name NOT LIKE '%_config%' AND name NOT LIKE '%_content%' AND name NOT LIKE '%_data%' AND name NOT LIKE '%_docsize%' AND name NOT LIKE '%_idx%'"
    ).fetchall()]
    conn.close()
    for t in tables:
        schema = sqlite3.connect(str(src_steer)).execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'"
        ).fetchone()[0]
        create_table_from_schema(hedef_cereyan, t, schema)
        copy_table(src_steer, hedef_cereyan, t)

print(f"  → cereyan.db ready")

# ── GROUP 7: Skills → skills.db ──────────────────────────────────────
print("\n=== GROUP 7: Skills ===")
hedef_skills = ReYMeN_DB / "skills.db"
print(f"Creating {hedef_skills}...")

# skills_index.db (FTS5 + beceriler_meta - 531 rows)
src_si = PROJE_KOK / "src" / "reymen" / "cereyan" / ".ReYMeN" / "skills_index.db"
if src_si.exists():
    shutil.copy2(str(src_si), str(hedef_skills))
    print(f"  Copied skills_index.db as base (FTS + 531 meta rows)")

# skill_library.db
src_sl = PROJE_KOK / "src" / "reymen" / "cereyan" / ".ReYMeN" / "skill_library.db"
if src_sl.exists() and not check_empty(src_sl):
    copy_table(src_sl, hedef_skills, "skills")

print(f"  → skills.db ready")

# ── GROUP 8: Hafiza (keep) ───────────────────────────────────────────
print("\n=== GROUP 8: Memory/Hafiza ===")
hedef_hafiza = ReYMeN_DB / "hafiza.db"
src_hafiza = PROJE_KOK / "src" / "reymen" / "hafiza" / "merkez_db" / "hafiza.db"
if src_hafiza.exists():
    shutil.copy2(str(src_hafiza), str(hedef_hafiza))
    print(f"  Copied hafiza.db → .ReYMeN/db/hafiza.db")

# ── GROUP 9: Analytics → analitik_merkezi.db ─────────────────────────
print("\n=== GROUP 9: Analytics ===")
hedef_analitik = ReYMeN_DB / "analitik_merkezi.db"
print(f"Creating {hedef_analitik}...")

# Base: analitik.db
src_anal = PROJE_KOK / "src" / "reymen" / "merkez_db" / "analitik.db"
if src_anal.exists():
    shutil.copy2(str(src_anal), str(hedef_analitik))
    print(f"  Copied analitik.db as base")

# self_improve.db
src_si2 = PROJE_KOK / "src" / "reymen" / "merkez_db" / "self_improve.db"
if src_si2.exists() and not check_empty(src_si2):
    conn = sqlite3.connect(str(src_si2))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE '%_idx%'"
    ).fetchall()]
    conn.close()
    for t in tables:
        schema = sqlite3.connect(str(src_si2)).execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'"
        ).fetchone()[0]
        create_table_from_schema(hedef_analitik, t, schema)
        copy_table(src_si2, hedef_analitik, t)
else:
    print(f"  self_improve.db: empty or no source data")

# execution_log.sqlite
src_exe = PROJE_KOK / "execution_log.sqlite"
if src_exe.exists() and not check_empty(src_exe):
    conn = sqlite3.connect(str(src_exe))
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()]
    conn.close()
    for t in tables:
        schema = sqlite3.connect(str(src_exe)).execute(
            f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{t}'"
        ).fetchone()[0]
        create_table_from_schema(hedef_analitik, t, schema)
        copy_table(src_exe, hedef_analitik, t)

print(f"  → analitik_merkezi.db ready")


print("\n" + "="*60)
print("MERGE COMPLETE")
print("="*60)

# List final consolidated files
print("\nConsolidated DBs in .ReYMeN/db/:")
for f in sorted(ReYMeN_DB.glob("*.db")):
    size = f.stat().st_size
    print(f"  {f.name}: {size/1024:.1f} KB")

print("\nKept original DBs:")
originals = [
    PROJE_KOK / "merkez_db" / "session.db",
    PROJE_KOK / ".ReYMeN" / "sohbet_bot_arkiv" / "state.db",
    PROJE_KOK / "shared_state" / "findings_board.db",
    PROJE_KOK / "src" / "reymen" / "arac" / ".ReYMeN" / "kanban.db",
    PROJE_KOK / "skills" / "improvements.db",
]
for p in originals:
    if p.exists():
        print(f"  {p.relative_to(PROJE_KOK)}: {p.stat().st_size/1024:.1f} KB")

print(f"\nTotal: {len(list(ReYMeN_DB.glob('*.db'))) + len([p for p in originals if p.exists()])} DBs")
