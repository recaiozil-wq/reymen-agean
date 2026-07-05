#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_sync_oncehafiza.py â€” Cron job: skills/.md -> OnceHafiza DB sync.

Her â”œÂºalâ”€â–’â”¼Æ’tâ”€â–’râ”€â–’lâ”€â–’â”¼Æ’â”€â–’nda:
  1. reymen/cereyan/skills/ altâ”€â–’ndaki tâ”œâ•m .md dosyalarâ”€â–’nâ”€â–’ tara
  2. SHA256 hash hesapla
  3. skill_hashes tablosuyla karâ”¼Æ’â”€â–’laâ”¼Æ’tâ”€â–’r:
     - Yeni dosya -> ogrenmeler + skill_hashes INSERT
     - Deâ”€Æ’iâ”¼Æ’en hash -> ogrenmeler UPDATE + skill_hashes UPDATE
     - Hash aynâ”€â–’ -> atla
  4. Rapor: kaâ”œÂº yeni, kaâ”œÂº gâ”œâ•ncellendi, kaâ”œÂº atlandâ”€â–’
"""

import hashlib
import os
import sqlite3
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# â”€â”€ Yollar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SCRIPT_DIR = Path(__file__).resolve().parent
CEREYAN_DIR = SCRIPT_DIR.parent.parent  # reymen/cereyan
SKILLS_ROOT = CEREYAN_DIR / "skills"
DB_PATH = CEREYAN_DIR / ".ReYMeN" / "ogrenmeler.db"
LOG_PATH = SCRIPT_DIR / "skill_sync_oncehafiza.log"

# fallback: goreceli yol calismazsa
if not SKILLS_ROOT.is_dir():
    SKILLS_ROOT = Path("reymen/cereyan/skills")
    CEREYAN_DIR = Path("reymen/cereyan")
    DB_PATH = CEREYAN_DIR / ".ReYMeN" / "ogrenmeler.db"


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")


def hash_file(path: Path) -> str:
    """SHA256 hash of file content."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def hedef_from_path(rel_path: str) -> str:
    """Derive 'hedef' from filename stem."""
    return Path(rel_path).stem


def kategori_from_path(rel_path: str) -> str:
    """Derive 'kategori' from the directory path relative to skills/ root."""
    p = Path(rel_path)
    parent = str(p.parent)
    if parent == ".":
        return "skills/genel"
    # Alt klasâ”œÃ‚rleri "skills/" ile baslat ve "/" -> "/" olarak koru
    return f"skills/{parent}"


def main():
    log(f"=== SKILL -> OnceHafiza Sync Basliyor ===")
    log(f"  Skills root: {SKILLS_ROOT}")
    log(f"  DB path:     {DB_PATH}")
    log(f"  Log path:    {LOG_PATH}")

    if not SKILLS_ROOT.is_dir():
        log(f"  HATA: Skills klasoru bulunamadi: {SKILLS_ROOT}")
        return 1

    if not DB_PATH.is_file():
        log(f"  HATA: DB dosyasi bulunamadi: {DB_PATH}")
        return 1

    # â”€â”€ 1. Tâ”œâ•m .md dosyalarâ”€â–’nâ”€â–’ tara â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    md_files = sorted(SKILLS_ROOT.rglob("*.md"))
    log(f"  Toplam .md dosyasi bulundu: {len(md_files)}")

    # â”€â”€ 2. DB'ye baâ”€Æ’lan â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    # skill_hashes tablosu yoksa olustur
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS skill_hashes (
            dosya_yolu  TEXT PRIMARY KEY,
            hash_256    TEXT NOT NULL,
            son_gorulme TEXT NOT NULL DEFAULT (datetime('now')),
            guncelleme  TEXT NOT NULL DEFAULT (datetime('now'))
        );
    """)
    conn.commit()

    # â”€â”€ 3. Mevcut hash'leri yukle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    mevcut_hashler = {}
    for row in conn.execute("SELECT dosya_yolu, hash_256 FROM skill_hashes"):
        mevcut_hashler[row["dosya_yolu"]] = row["hash_256"]
    log(f"  Mevcut skill_hashes kaydi: {len(mevcut_hashler)}")

    # â”€â”€ 4. Her dosyayi isle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    yeni = 0
    guncellenen = 0
    atlanan = 0
    hata = 0

    bugun = date.today().isoformat()
    gecerlilik = (date.today() + timedelta(days=180)).isoformat()
    simdi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for fp in md_files:
        try:
            rel = str(fp.relative_to(SKILLS_ROOT).as_posix())
        except Exception as e:
            log(f"  HATA (rel path) [{fp}]: {e}")
            hata += 1
            continue

        try:
            h = hash_file(fp)
        except Exception as e:
            log(f"  HATA (hash) [{rel}]: {e}")
            hata += 1
            continue

        eski_hash = mevcut_hashler.get(rel)

        if eski_hash == h:
            # Hash ayni -> sadece son_gorulme guncelle
            conn.execute(
                "UPDATE skill_hashes SET son_gorulme = datetime('now') WHERE dosya_yolu = ?",
                (rel,),
            )
            conn.commit()
            atlanan += 1
            continue

        # â”€â”€ Hedef ve kategori hesapla â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        hedef = hedef_from_path(rel)
        kategori = kategori_from_path(rel)
        try:
            icerik = fp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            log(f"  HATA (okuma) [{rel}]: {e}")
            hata += 1
            continue

        if eski_hash is None:
            # â”€â”€ YENI DOSYA -> INSERT into both tables â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            try:
                conn.execute(
                    """INSERT INTO ogrenmeler
                       (hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi,
                        son_kullanim, gecerlilik_tarihi, olusturulma, guncelleme)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        hedef,
                        kategori,
                        icerik,
                        0.5,  # baslangic guven
                        1,
                        0,  # basari=1, hata=0
                        bugun,
                        gecerlilik,
                        simdi,
                        simdi,
                    ),
                )
                conn.execute(
                    """INSERT INTO skill_hashes (dosya_yolu, hash_256, son_gorulme, guncelleme)
                       VALUES (?, ?, datetime('now'), datetime('now'))""",
                    (rel, h),
                )
                conn.commit()
                yeni += 1
                log(f"  + YENI  [{rel}] -> hedef='{hedef}' kategori='{kategori}'")
            except sqlite3.IntegrityError as e:
                # hedef+kategori unique degil -> bul ve guncelle
                log(f"  INTEGRITY [{rel}]: {e} -> guncelleme dene")
                conn.rollback()
                try:
                    existing = conn.execute(
                        "SELECT id FROM ogrenmeler WHERE hedef = ? AND kategori = ?",
                        (hedef, kategori),
                    ).fetchone()
                    if existing:
                        conn.execute(
                            """UPDATE ogrenmeler SET
                                icerik = ?, guncelleme = ?, son_kullanim = ?
                               WHERE id = ?""",
                            (icerik, simdi, bugun, existing["id"]),
                        )
                        conn.execute(
                            """INSERT OR REPLACE INTO skill_hashes (dosya_yolu, hash_256, son_gorulme, guncelleme)
                               VALUES (?, ?, datetime('now'), datetime('now'))""",
                            (rel, h),
                        )
                        conn.commit()
                        guncellenen += 1
                        log(f"  ~ GUNCELLENDI (integrity) [{rel}]")
                    else:
                        log(f"  HATA [{rel}]: Integrity hatasi ama kayit bulunamadi")
                        conn.rollback()
                        hata += 1
                except Exception as e2:
                    conn.rollback()
                    log(f"  HATA (kurtarma) [{rel}]: {e2}")
                    hata += 1
        else:
            # â”€â”€ VAR OLAN DOSYA -> hash degismis -> guncelle â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            try:
                existing = conn.execute(
                    "SELECT id FROM ogrenmeler WHERE hedef = ? AND kategori = ?",
                    (hedef, kategori),
                ).fetchone()
                if existing:
                    conn.execute(
                        """UPDATE ogrenmeler SET
                            icerik = ?, guncelleme = ?, son_kullanim = ?
                           WHERE id = ?""",
                        (icerik, simdi, bugun, existing["id"]),
                    )
                else:
                    # Hedef+kategori yoksa -> INSERT (dosya yeniden tasinmis olabilir)
                    conn.execute(
                        """INSERT INTO ogrenmeler
                           (hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi,
                            son_kullanim, gecerlilik_tarihi, olusturulma, guncelleme)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            hedef,
                            kategori,
                            icerik,
                            0.5,
                            1,
                            0,
                            bugun,
                            gecerlilik,
                            simdi,
                            simdi,
                        ),
                    )

                conn.execute(
                    """UPDATE skill_hashes SET
                        hash_256 = ?, son_gorulme = datetime('now'), guncelleme = datetime('now')
                       WHERE dosya_yolu = ?""",
                    (h, rel),
                )
                conn.commit()
                guncellenen += 1
                log(f"  ~ GUNCELLENDI [{rel}] -> hash degisti")
            except Exception as e:
                conn.rollback()
                log(f"  HATA (guncelleme) [{rel}]: {e}")
                hata += 1

    # â”€â”€ 5. Temizlik: skill_hashes'te olup skills klasorunde olmayan kayitlari sil
    tum_rel_paths = set()
    for fp in md_files:
        try:
            tum_rel_paths.add(str(fp.relative_to(SKILLS_ROOT).as_posix()))
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

    silinen_kayitlar = 0
    for row in conn.execute("SELECT dosya_yolu FROM skill_hashes"):
        if row["dosya_yolu"] not in tum_rel_paths:
            conn.execute(
                "DELETE FROM skill_hashes WHERE dosya_yolu = ?", (row["dosya_yolu"],)
            )
            silinen_kayitlar += 1
    if silinen_kayitlar > 0:
        conn.commit()
        log(f"  - Silinen dosya kayitlari temizlendi: {silinen_kayitlar}")

    conn.close()

    # â”€â”€ 6. Rapor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    log(f"=== SKILL -> OnceHafiza Sync Tamam ===")
    log(f"  YENI eklenen:    {yeni}")
    log(f"  GUNCELLENEN:     {guncellenen}")
    log(f"  ATLANAN (ayni):  {atlanan}")
    log(f"  HATA:            {hata}")
    log(f"  Silinen kayit:   {silinen_kayitlar}")
    log(f"  Toplam dosya:    {len(md_files)}")

    # Son satir ozet - cron delivery icin
    print(
        f"\nOZET: +{yeni} yeni / ~{guncellenen} guncellendi / -{atlanan} ayni / !{hata} hata / Silinen: {silinen_kayitlar}"
    )

    # Raporu decisions.md'ye de ekle
    karar_yolu = CEREYAN_DIR / ".ReYMeN" / "decisions.md"
    try:
        with open(karar_yolu, "a", encoding="utf-8") as f:
            f.write(f"## {simdi[:10]} {simdi[11:16]} â€” Skill -> OnceHafiza Sync\n")
            f.write(
                f"- Yeni: {yeni}, Guncellenen: {guncellenen}, Atanan: {atlanan}, Hata: {hata}\n"
            )
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    return 0


if __name__ == "__main__":
    sys.exit(main())
