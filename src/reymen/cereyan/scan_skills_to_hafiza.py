# -*- coding: utf-8 -*-
"""
scan_skills_to_hafiza.py â€” reymen/cereyan/skills/ klasÃ¶rÃ¼ndeki .md dosyalarÄ±nÄ±
tara, skills_index.db'deki beceriler_meta tablosuyla karÅŸÄ±laÅŸtÄ±r.
  - Eksik olanlarÄ± EKLE (yeni)
  - Hash deÄŸiÅŸmiÅŸ olanlarÄ± GÃœNCELLE (gÃ¼ncellenmiÅŸ)
  - DeÄŸiÅŸmeyenleri ATLA

Her 6 saatte bir Ã§alÄ±ÅŸacak cron job.
"""

import hashlib
import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("scan_skills")

# â”€â”€ Yollar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
ROOT = Path(__file__).parent.parent.resolve()  # reymen/
SKILLS_DIR = ROOT / "cereyan" / "skills"  # taranacak klasÃ¶r
SKILLS_DB = ROOT.parent / ".ReYMeN" / "db" / "skills.db"  # consolidated: skills_index + skill_library
OGRENME_DB = ROOT.parent / ".ReYMeN" / "db" / "ogrenme_merkezi.db"  # consolidated: ogrenme.db + ogrenmeler.db + proaktif_ogrenme


def dosya_hash(dosya_yolu: str) -> str:
    """Bir dosyanÄ±n SHA256 hash'ini dÃ¶ndÃ¼r (ilk 16 karakter)."""
    h = hashlib.sha256()
    with open(dosya_yolu, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def kategori_ve_ad(dosya_yolu: str) -> tuple[str, str]:
    """
    GÃ¶reli yoldan kategori ve dosya adÄ±nÄ± Ã§Ä±kar.
    Ã–rn: 'AI_ML/agents/agent-project-bootstrap.md' â†’ ('AI_ML/agents', 'agent-project-bootstrap.md')
    """
    rel = os.path.relpath(dosya_yolu, str(SKILLS_DIR))
    rel = rel.replace("\\", "/")
    parts = rel.split("/")
    if len(parts) == 1:
        return "", parts[0]
    else:
        return "/".join(parts[:-1]), parts[-1]


def beceriden_aciklama_ve_icerik(icerik: str) -> tuple[str, str]:
    """
    Markdown iÃ§eriÄŸinden:
    - aciklama: ilk satÄ±r (# ile baÅŸlayan baÅŸlÄ±k) veya ilk 200 karakter
    - icerik: tÃ¼m iÃ§erik
    """
    lines = icerik.split("\n")
    baslik = ""
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            baslik = line[2:].strip()
            break
    if not baslik:
        baslik = icerik[:200].strip()
    return baslik, icerik


def scan_skills():
    """Ana tarama fonksiyonu."""
    logger.info("=" * 60)
    logger.info("ğŸ” Skills tarama baÅŸlÄ±yor...")
    logger.info("   KlasÃ¶r: %s", SKILLS_DIR)
    logger.info("   DB:     %s", SKILLS_DB)
    logger.info("   Ã–ÄŸrenme: %s", OGRENME_DB)

    # 1) Skills dizinindeki tÃ¼m .md dosyalarÄ±nÄ± bul
    md_dosyalari = sorted(SKILLS_DIR.rglob("*.md"))
    logger.info("ğŸ“„ Skills klasÃ¶rÃ¼nde %d .md dosyasÄ± bulundu.", len(md_dosyalari))

    # 2) Skills DB'deki mevcut meta tablosunu yÃ¼kle
    con = sqlite3.connect(str(SKILLS_DB))
    con.execute("PRAGMA journal_mode=WAL")

    # Meta tablosunda ne var kontrol et
    meta_cur = con.execute("SELECT ad, dosya_hash FROM beceriler_meta")
    meta_map = {}  # ad -> hash
    for row in meta_cur.fetchall():
        meta_map[row[0]] = row[1]
    logger.info("ğŸ“š Skills DB'de %d kayÄ±tlÄ± dosya var.", len(meta_map))

    con.close()

    # 3) Her dosyayÄ± kontrol et
    yeni_sayisi = 0
    guncel_sayisi = 0
    atlanan_sayisi = 0

    for dosya in md_dosyalari:
        kategori, dosya_adi = kategori_ve_ad(str(dosya))
        # Meta tablosundaki ad formatÄ±: "kategori/dosya_adi" veya "dosya_adi"
        meta_adi = f"{kategori}/{dosya_adi}" if kategori else dosya_adi

        # DosyanÄ±n hash'ini hesapla
        try:
            guncel_hash = dosya_hash(str(dosya))
        except (OSError, IOError) as e:
            logger.warning("âš ï¸  Dosya okunamadÄ±: %s â€” %s", dosya, e)
            continue

        # Mevcut hash ile karÅŸÄ±laÅŸtÄ±r
        eski_hash = meta_map.get(meta_adi)

        if eski_hash is None:
            # YENÄ° DOSYA
            logger.info("ğŸ†• YENÄ°: %s", meta_adi)
            yeni_sayisi += 1
            _skills_db_ekle(meta_adi, str(dosya), guncel_hash)
            _ogrenme_db_ekle(kategori, dosya_adi, str(dosya))
        elif eski_hash != guncel_hash:
            # GÃœNCELLENMÄ°Å DOSYA
            logger.info(
                "ğŸ”„ GÃœNCELLENMÄ°Å: %s (hash: %s â†’ %s)", meta_adi, eski_hash, guncel_hash
            )
            guncel_sayisi += 1
            _skills_db_guncelle(meta_adi, str(dosya), guncel_hash)
            _ogrenme_db_guncelle(kategori, dosya_adi, str(dosya))
        else:
            atlanan_sayisi += 1

    logger.info("=" * 60)
    logger.info("âœ… Tarama tamamlandÄ±!")
    logger.info("   Yeni eklenen:  %d", yeni_sayisi)
    logger.info("   GÃ¼ncellenen:   %d", guncel_sayisi)
    logger.info("   Atlanan (aynÄ±): %d", atlanan_sayisi)
    logger.info("=" * 60)

    return yeni_sayisi, guncel_sayisi, atlanan_sayisi


def _skills_db_ekle(meta_adi: str, dosya_yolu: str, dosya_hash_val: str):
    """Yeni dosyayÄ± skills_index.db'ye ekle (FTS5 + meta)."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except Exception as e:
        logger.warning("âš ï¸  Ä°Ã§erik okunamadÄ±: %s â€” %s", dosya_yolu, e)
        return

    baslik, tam_icerik = beceriden_aciklama_ve_icerik(icerik)
    muhtemel_aciklama = baslik[:500] if len(baslik) > 500 else baslik
    muhtemel_icerik = tam_icerik[:10000] if len(tam_icerik) > 10000 else tam_icerik

    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con = sqlite3.connect(str(SKILLS_DB))
    try:
        # FTS5 tablosuna ekle
        con.execute(
            "INSERT INTO beceriler (ad, aciklama, icerik, kaynak) VALUES (?, ?, ?, ?)",
            (meta_adi, muhtemel_aciklama, muhtemel_icerik, dosya_yolu),
        )
        # Meta tablosuna ekle
        con.execute(
            "INSERT INTO beceriler_meta (ad, dosya_hash, guncelleme) VALUES (?, ?, ?)",
            (meta_adi, dosya_hash_val, su_an),
        )
        con.commit()
    except sqlite3.IntegrityError:
        # Ad zaten varsa update yap
        con.execute(
            "UPDATE beceriler SET aciklama=?, icerik=?, kaynak=? WHERE ad=?",
            (muhtemel_aciklama, muhtemel_icerik, dosya_yolu, meta_adi),
        )
        con.execute(
            "UPDATE beceriler_meta SET dosya_hash=?, guncelleme=? WHERE ad=?",
            (dosya_hash_val, su_an, meta_adi),
        )
        con.commit()
    finally:
        con.close()


def _skills_db_guncelle(meta_adi: str, dosya_yolu: str, dosya_hash_val: str):
    """Mevcut dosyayÄ± skills_index.db'de gÃ¼ncelle."""
    try:
        with open(dosya_yolu, "r", encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except Exception as e:
        logger.warning("âš ï¸  Ä°Ã§erik okunamadÄ±: %s â€” %s", dosya_yolu, e)
        return

    baslik, tam_icerik = beceriden_aciklama_ve_icerik(icerik)
    muhtemel_aciklama = baslik[:500]
    muhtemel_icerik = tam_icerik[:10000]
    su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    con = sqlite3.connect(str(SKILLS_DB))
    try:
        # FTS5'te gÃ¼ncelle (ad'a gÃ¶re)
        con.execute(
            "UPDATE beceriler SET aciklama=?, icerik=?, kaynak=? WHERE ad=?",
            (muhtemel_aciklama, muhtemel_icerik, dosya_yolu, meta_adi),
        )
        # Meta gÃ¼ncelle
        con.execute(
            "UPDATE beceriler_meta SET dosya_hash=?, guncelleme=? WHERE ad=?",
            (dosya_hash_val, su_an, meta_adi),
        )
        con.commit()
    finally:
        con.close()


def _ogrenme_db_ekle(kategori: str, dosya_adi: str, dosya_yolu: str):
    """
    Yeni skill dosyasÄ±nÄ± OnceHafiza ogrenme DB'sine (ogrenme.db) kaydet.
    """
    try:
        with open(dosya_yolu, "r", encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except Exception as e:
        logger.warning("âš ï¸  ogrenme.db ekleme: iÃ§erik okunamadÄ±: %s", e)
        return

    hedef = dosya_adi.replace(".md", "")
    cozum = icerik[:5000] if len(icerik) > 5000 else icerik
    kaynak = "skills_scan"
    kat = kategori if kategori else "genel"

    con = sqlite3.connect(str(OGRENME_DB))
    try:
        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        con.execute(
            """INSERT INTO ogrenmeler
               (hedef, cozum, kaynak, basari_sayisi, son_basari, son_kullanim,
                guven_skoru, kategori, gecerlilik_tarihi)
               VALUES (?, ?, ?, 1, ?, ?, 0.5, ?, ?)
               ON CONFLICT(hedef) DO UPDATE SET
                cozum = excluded.cozum,
                son_basari = excluded.son_basari,
                son_kullanim = excluded.son_kullanim,
                guven_skoru = MAX(0.5, guven_skoru),
                kategori = CASE WHEN excluded.kategori != '' THEN excluded.kategori ELSE kategori END""",
            (hedef, cozum, kaynak, su_an, su_an, kat, su_an),
        )
        con.commit()
    except Exception as e:
        logger.warning("âš ï¸  ogrenme.db ekleme hatasÄ± (%s): %s", hedef, e)
    finally:
        con.close()


def _ogrenme_db_guncelle(kategori: str, dosya_adi: str, dosya_yolu: str):
    """
    GÃ¼ncellenmiÅŸ skill dosyasÄ±nÄ± OnceHafiza ogrenme DB'sinde gÃ¼ncelle.
    """
    try:
        with open(dosya_yolu, "r", encoding="utf-8", errors="replace") as f:
            icerik = f.read()
    except Exception as e:
        logger.warning("âš ï¸  ogrenme.db gÃ¼ncelleme: iÃ§erik okunamadÄ±: %s", e)
        return

    hedef = dosya_adi.replace(".md", "")
    cozum = icerik[:5000] if len(icerik) > 5000 else icerik
    kat = kategori if kategori else "genel"

    con = sqlite3.connect(str(OGRENME_DB))
    try:
        su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Ã–nce var mÄ± kontrol et
        var = con.execute(
            "SELECT id FROM ogrenmeler WHERE hedef = ?", (hedef,)
        ).fetchone()
        if var:
            con.execute(
                """UPDATE ogrenmeler SET
                    cozum = ?,
                    kategori = ?,
                    son_basari = ?,
                    son_kullanim = ?,
                    gecerlilik_tarihi = datetime('now', '+180 days')
                   WHERE hedef = ?""",
                (cozum, kat, su_an, su_an, hedef),
            )
        else:
            con.execute(
                """INSERT INTO ogrenmeler
                   (hedef, cozum, kaynak, basari_sayisi, son_basari, son_kullanim,
                    guven_skoru, kategori, gecerlilik_tarihi)
                   VALUES (?, ?, 'skills_scan', 1, ?, ?, 0.5, ?, datetime('now', '+180 days'))""",
                (hedef, cozum, su_an, su_an, kat),
            )
        con.commit()
    except Exception as e:
        logger.warning("âš ï¸  ogrenme.db gÃ¼ncelleme hatasÄ± (%s): %s", hedef, e)
    finally:
        con.close()


if __name__ == "__main__":
    yeni, guncel, atlanan = scan_skills()
    # Ã‡Ä±ktÄ±: makine tarafÄ±ndan okunabilir format
    print(f"SONUC|new={yeni}|updated={guncel}|skipped={atlanan}")
