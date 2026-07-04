# -*- coding: utf-8 -*-
"""
once_hafiza.py — Memory-first execution engine.

Every task first checks memory, directly applies known information,
or tries it and saves the result if not found.

Usage:
    sonuc = once_hafiza.isle(
        hedef="nmap ile port tara",
        kategori="kali/network",
        calistir=lambda: kali_sandbox.calistir("nmap --help")
    )
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# ── Varsayılan yol ────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.resolve()
DB_YOLU = ROOT.parent / "merkez_db" / "ogrenmeler.db"

# 6 ay = ~180 gün
GECERLILIK_GUN = 180

_yazma_kilit = threading.Lock()


# ── Kademeli Güven Fonksiyonu ─────────────────────────────────────────────


def _kademeli_guven(basari: int, hata: int) -> float:
    """
    Sigmoid-like gradual confidence calculation.

    First success: 0.5, 3 successes: ~0.75, 10 successes: ~0.95.
    Confidence decreases as error rate increases.

    Formula: 1 / (1 + e^(-0.5 * (basari - hata - 1)))
    - First record (1 success, 0 errors): 0.5
    - 3 successes, 0 errors: ~0.73
    - 10 successes, 0 errors: ~0.99
    - 1 success, 3 errors: ~0.12
    """
    import math

    net = basari - hata - 1  # -1 offset: ilk kayıtta 0.5
    return 1.0 / (1.0 + math.exp(-0.5 * net))


# ── Veritabanı ────────────────────────────────────────────────────────────


def _kur(con: sqlite3.Connection) -> None:
    """Create the ogrenmeler table."""
    con.executescript("""
        CREATE TABLE IF NOT EXISTS ogrenmeler (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            hedef           TEXT NOT NULL,
            kategori        TEXT NOT NULL DEFAULT 'genel',
            icerik          TEXT NOT NULL,
            guven_skoru     REAL NOT NULL DEFAULT 1.0,
            basari_sayisi   INTEGER NOT NULL DEFAULT 1,
            hata_sayisi     INTEGER NOT NULL DEFAULT 0,
            son_kullanim    TEXT NOT NULL DEFAULT (date('now')),
            gecerlilik_tarihi TEXT NOT NULL DEFAULT (date('now', '+180 days')),
            kaynak_url      TEXT DEFAULT NULL,
            olusturulma     TEXT NOT NULL DEFAULT (datetime('now')),
            guncelleme      TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_ogrenmeler_kategori ON ogrenmeler(kategori);
        CREATE INDEX IF NOT EXISTS idx_ogrenmeler_hedef   ON ogrenmeler(hedef);
        CREATE INDEX IF NOT EXISTS idx_ogrenmeler_gecerli ON ogrenmeler(gecerlilik_tarihi);
    """)

    # Migration: eski tablolara kaynak_url ekle (güvenli, sadece yoksa)
    try:
        con.execute("ALTER TABLE ogrenmeler ADD COLUMN kaynak_url TEXT DEFAULT NULL")
    except Exception as _e:
        err_msg = str(_e)
        if "duplicate column" not in err_msg.lower():
            __import__("logging").getLogger(__name__).warning(
                "[SessizExcept] %s: %s", type(_e).__name__, err_msg
            )


@contextmanager
def _baglanti():
    con = sqlite3.connect(str(DB_YOLU), timeout=15, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def _db_kur():
    DB_YOLU.parent.mkdir(parents=True, exist_ok=True)
    with _baglanti() as con:
        _kur(con)


# ── Ana API ───────────────────────────────────────────────────────────────


def kaydet(
    hedef: str,
    kategori: str = "genel",
    icerik: str = "",
    basari: bool = True,
    gecerlilik_gun: int = GECERLILIK_GUN,
    kaynak_url: str | None = None,
) -> int:
    """
    Create a new learning record or update if it already exists.

    Args:
        hedef: Task description (e.g. "scan ports with nmap")
        kategori: "kali", "dron", "cad", "kali/network" etc.
        icerik: Learned information / solution
        basari: Was it successful?
        gecerlilik_gun: Validity duration in days (default: 180)
        kaynak_url: Source of the information (web URL) (default: None)

    Returns:
        Record ID
    """
    _db_kur()
    bugun = date.today().isoformat()
    gecerlilik = (date.today() + timedelta(days=gecerlilik_gun)).isoformat()

    with _yazma_kilit:
        with _baglanti() as con:
            # Daha önce aynı hedef+kategori var mı?
            var = con.execute(
                "SELECT id, basari_sayisi, hata_sayisi, guven_skoru FROM ogrenmeler "
                "WHERE hedef = ? AND kategori = ? LIMIT 1",
                (hedef, kategori),
            ).fetchone()

            if var:
                kayit_id, basari_once, hata_once, guven_once = var
                yeni_basari = basari_once + (1 if basari else 0)
                yeni_hata = hata_once + (0 if basari else 1)
                toplam = yeni_basari + yeni_hata
                # Kademeli güven: sigmoid benzeri, 3 başarıda ~0.75
                guven = round(_kademeli_guven(yeni_basari, yeni_hata), 4)

                con.execute(
                    """UPDATE ogrenmeler SET
                        icerik = ?,
                        guven_skoru = ?,
                        basari_sayisi = ?,
                        hata_sayisi = ?,
                        son_kullanim = ?,
                        gecerlilik_tarihi = ?,
                        kaynak_url = COALESCE(?, kaynak_url),
                        guncelleme = datetime('now')
                    WHERE id = ?""",
                    (
                        icerik,
                        guven,
                        yeni_basari,
                        yeni_hata,
                        bugun,
                        gecerlilik,
                        kaynak_url,
                        kayit_id,
                    ),
                )
                logger.info(
                    "[Hafiza] Guncellendi: %s/%s (guven=%.2f, %d basari, %d hata)",
                    kategori,
                    hedef[:40],
                    guven,
                    yeni_basari,
                    yeni_hata,
                )
                return kayit_id
            else:
                # İlk kayıt: guven=0.5 başlangıç, kademeli artar
                baslangic_guven = 0.5 if basari else 0.1
                con.execute(
                    """INSERT INTO ogrenmeler
                       (hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi,
                        son_kullanim, gecerlilik_tarihi, kaynak_url)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        hedef,
                        kategori,
                        icerik,
                        baslangic_guven,
                        1 if basari else 0,
                        0 if basari else 1,
                        bugun,
                        gecerlilik,
                        kaynak_url,
                    ),
                )
                kayit_id = con.execute("SELECT last_insert_rowid()").fetchone()[0]
                logger.info(
                    "[Hafiza] Yeni kayit: %s/%s (id=%d, guven=%.2f)",
                    kategori,
                    hedef[:40],
                    kayit_id,
                    baslangic_guven,
                )
                return kayit_id


def ara(
    hedef: str,
    kategori: str | None = None,
    min_guven: float = 0.3,
    gecerli_mi: bool = True,
) -> list[dict[str, Any]]:
    """
    Search memory for similar tasks/solutions.

    Each result has a `durum` field:
      - "guvenilir" → guven_skoru >= 0.5
      - "belirsiz"  → guven_skoru < 0.5

    Args:
        hedef: Task to search for
        kategori: Filter by category (None = all)
        min_guven: Minimum confidence score (0.0-1.0)
        gecerli_mi: Only return records that haven't expired?

    Returns:
        [{"id", "hedef", "kategori", "icerik", "guven_skoru", "durum",
          "son_kullanim", "gecerlilik_tarihi", ...}, ...]
    """
    _db_kur()
    kosullar = ["guven_skoru >= ?"]
    params: list[Any] = [min_guven]

    if kategori:
        kosullar.append("kategori = ?")
        params.append(kategori)

    if gecerli_mi:
        kosullar.append("gecerlilik_tarihi >= date('now')")

    # Tam eşleşme önce, sonra LIKE
    with _baglanti() as con:
        # 1) Tam eşleşme
        tam_sql = (
            "SELECT id, hedef, kategori, icerik, guven_skoru, "
            "basari_sayisi, hata_sayisi, son_kullanim, gecerlilik_tarihi, kaynak_url "
            "FROM ogrenmeler WHERE hedef = ? AND {} "
            "ORDER BY guven_skoru DESC, son_kullanim DESC LIMIT 5"
        ).format(" AND ".join(kosullar))
        tam = con.execute(tam_sql, [hedef] + params).fetchall()

        # 2) Benzer (LIKE)
        benzer_sql = (
            "SELECT id, hedef, kategori, icerik, guven_skoru, "
            "basari_sayisi, hata_sayisi, son_kullanim, gecerlilik_tarihi, kaynak_url "
            "FROM ogrenmeler WHERE hedef LIKE ? AND {} "
            "ORDER BY guven_skoru DESC, son_kullanim DESC LIMIT 5"
        ).format(" AND ".join(kosullar))
        benzer = con.execute(benzer_sql, ["%{}%".format(hedef)] + params).fetchall()

    # Birleştir, duplicate'leri at
    gorulen: set[int] = set()
    sonuc = []
    for row in tam + benzer:
        if row[0] not in gorulen:
            gorulen.add(row[0])
            guven = row[4]
            sonuc.append(
                {
                    "id": row[0],
                    "hedef": row[1],
                    "kategori": row[2],
                    "icerik": row[3],
                    "guven_skoru": guven,
                    "durum": "guvenilir" if guven >= 0.5 else "belirsiz",
                    "basari_sayisi": row[5],
                    "hata_sayisi": row[6],
                    "son_kullanim": row[7],
                    "gecerlilik_tarihi": row[8],
                    "kaynak_url": row[9] if len(row) > 9 else None,
                }
            )

    return sonuc


def hafizada_ara(
    hedef: str,
    kategori: str | None = None,
    min_guven: float = 0.3,
    gecerli_mi: bool = True,
) -> list[dict[str, Any]]:
    """Alias: same as ara(). Works when user calls 'hafizada_ara()'."""
    return ara(hedef, kategori, min_guven, gecerli_mi)


def guven_guncelle(kayit_id: int, basari: bool) -> float:
    """
    Update a record's confidence score based on success/failure count.

    Returns:
        New confidence score
    """
    with _yazma_kilit:
        with _baglanti() as con:
            var = con.execute(
                "SELECT basari_sayisi, hata_sayisi FROM ogrenmeler WHERE id = ?",
                (kayit_id,),
            ).fetchone()
            if not var:
                return 0.0

            yeni_basari = var[0] + (1 if basari else 0)
            yeni_hata = var[1] + (0 if basari else 1)
            # Kademeli güven (sigmoid)
            guven = round(_kademeli_guven(yeni_basari, yeni_hata), 4)

            con.execute(
                """UPDATE ogrenmeler SET
                    guven_skoru = ?,
                    basari_sayisi = ?,
                    hata_sayisi = ?,
                    son_kullanim = date('now'),
                    guncelleme = datetime('now')
                WHERE id = ?""",
                (guven, yeni_basari, yeni_hata, kayit_id),
            )

            if basari:
                logger.info("[Hafiza] Basari +1 (id=%d, guven=%.2f)", kayit_id, guven)
            else:
                logger.info("[Hafiza] Hata +1 (id=%d, guven=%.2f)", kayit_id, guven)

            return guven


def eski_kayitlari_temizle(gun_limiti: int = 200) -> int:
    """
    Remove expired records whose validity date has passed.
    But keep high-confidence ones (>=0.8).

    Returns:
        Number of deleted records
    """
    _db_kur()
    with _yazma_kilit:
        with _baglanti() as con:
            sil = con.execute(
                "DELETE FROM ogrenmeler "
                "WHERE gecerlilik_tarihi < date('now', ?) AND guven_skoru < 0.8",
                ("-{} days".format(gun_limiti),),
            ).rowcount
            if sil:
                logger.info("[Hafiza] %d eski kayit temizlendi.", sil)
            return sil


def isle(
    hedef: str,
    kategori: str = "genel",
    calistir: Callable[[], T] | None = None,
    min_guven: float = 0.5,
    gecerli_mi: bool = True,
    zorla: bool = False,
) -> tuple[T | dict | None, str]:
    """
    *** MAIN API — Memory-first task execution ***

    Flow:
        1. Search memory for similar task
        2a. Found + confidence >= min_guven + valid → return from cache
        2b. Not found or low confidence → run calistir() function
        3. Save result to memory
        4. Return result

    Args:
        hedef: Task description
        kategori: Category
        calistir: Function to execute (None = query memory only)
        min_guven: Minimum confidence for cache
        gecerli_mi: Check validity?
        zorla: True = skip memory, execute directly

    Returns:
        (result, source)
        result: Value from calistir() or memory record
        source: "cache" (from memory) / "exec" (executed) / "not_found"
    """
    _db_kur()

    if not zorla:
        kayitlar = ara(hedef, kategori, min_guven=min_guven, gecerli_mi=gecerli_mi)
        if kayitlar:
            en_iyi = kayitlar[0]
            logger.info(
                "[Hafiza] ONBELLEK: %s/%s (guven=%.2f)",
                en_iyi["kategori"],
                en_iyi["hedef"][:40],
                en_iyi["guven_skoru"],
            )
            # Kullanım güncelle
            guven_guncelle(en_iyi["id"], basari=True)

            if calistir is None:
                # Sadece hafıza sorgulama modu
                return en_iyi, "cache"

            # Önbellekte var ama yine de çalıştır? Hayır — direkt döndür
            return en_iyi, "cache"

    if calistir is None:
        return None, "not_found"

    # Çalıştır
    try:
        sonuc = calistir()
        kaydet(hedef, kategori, str(sonuc)[:5000] if sonuc else "", basari=True)
        return sonuc, "exec"
    except Exception as e:
        hata_mesaji = "[HATA] {}: {}".format(type(e).__name__, e)
        logger.warning(
            "[Hafiza] Basarisiz: %s/%s — %s", kategori, hedef[:40], hata_mesaji
        )
        kaydet(hedef, kategori, hata_mesaji, basari=False)
        raise


def istatistik() -> dict[str, Any]:
    """Memory statistics."""
    _db_kur()
    with _baglanti() as con:
        toplam = con.execute("SELECT COUNT(*) FROM ogrenmeler").fetchone()[0]
        gecerli = con.execute(
            "SELECT COUNT(*) FROM ogrenmeler WHERE gecerlilik_tarihi >= date('now')"
        ).fetchone()[0]
        eski = con.execute(
            "SELECT COUNT(*) FROM ogrenmeler WHERE gecerlilik_tarihi < date('now')"
        ).fetchone()[0]
        kategori_say = con.execute(
            "SELECT kategori, COUNT(*) FROM ogrenmeler GROUP BY kategori ORDER BY COUNT(*) DESC"
        ).fetchall()
        ortalama_guven = (
            con.execute("SELECT ROUND(AVG(guven_skoru), 4) FROM ogrenmeler").fetchone()[
                0
            ]
            or 0.0
        )

    return {
        "toplam": toplam,
        "gecerli": gecerli,
        "eski": eski,
        "ortalama_guven": ortalama_guven,
        "kategori_dagilimi": {k: v for k, v in kategori_say},
    }


# ── Belirsiz Görev Çözümleme ──────────────────────────────────────────────


def belirsiz_gorev_cozumle(
    hedef: str,
    esik: float = 0.3,
    max_kategori: int = 3,
) -> dict[str, Any]:
    """
    When an ambiguous task comes in, finds the most relevant category in memory
    and prepares a single guess suggestion for the user.

    Flow:
        1. Split the task into keywords
        2. Scan records under each category
        3. Find the most relevant category + matching record
        4. Return in question format to the user

    Args:
        hedef: The user's ambiguous task (e.g. "make the system secure")
        esik: Minimum similarity threshold (0.0-1.0)
        max_kategori: Maximum number of alternative categories to suggest

    Returns:
        {
            "tahmin_kategori": "kali/network" or None,
            "tahmin_kayit": {...} or None,
            "guven": 0.75,
            "alternatifler": [...],
            "soru": "I think you want to do a port scan, is that correct?",
            "ham_hedef": "make the system secure"
        }
    """
    _db_kur()

    # 1) Görevi normalize et ve anahtar kelimelere ayır
    kelimeler = _anahtar_kelimeler(hedef)
    if not kelimeler:
        return {
            "tahmin_kategori": None,
            "tahmin_kayit": None,
            "guven": 0.0,
            "alternatifler": [],
            "soru": None,
            "ham_hedef": hedef,
        }

    with _baglanti() as con:
        # 2) Tüm geçerli kayıtları çek
        tum_kayitlar = con.execute(
            "SELECT id, hedef, kategori, icerik, guven_skoru, basari_sayisi, hata_sayisi "
            "FROM ogrenmeler WHERE gecerlilik_tarihi >= date('now') "
            "ORDER BY guven_skoru DESC, basari_sayisi DESC"
        ).fetchall()

    if not tum_kayitlar:
        return {
            "tahmin_kategori": None,
            "tahmin_kayit": None,
            "guven": 0.0,
            "alternatifler": [],
            "soru": None,
            "ham_hedef": hedef,
        }

    # 3) Her kaydın görevle benzerlik skorunu hesapla
    skorlu: list[tuple[float, dict[str, Any]]] = []
    for row in tum_kayitlar:
        kayit = {
            "id": row[0],
            "hedef": row[1],
            "kategori": row[2],
            "icerik": row[3][:200],
            "guven_skoru": row[4],
            "basari_sayisi": row[5],
            "hata_sayisi": row[6],
        }
        skor = _benzerlik_skoru(hedef, kelimeler, kayit)
        if skor >= esik:
            skorlu.append((skor, kayit))

    # 4) Skora göre sırala
    skorlu.sort(key=lambda x: x[0], reverse=True)

    # 4b) Hiç kelime eşleşmezse en yüksek güvenli kaydı öner (backup)
    if not skorlu:
        # Güven skoru >= 0.8 olan en iyi kaydı bul
        en_guvenli = max(tum_kayitlar, key=lambda r: r[4]) if tum_kayitlar else None
        if en_guvenli and en_guvenli[4] >= 0.8:
            kayit = {
                "id": en_guvenli[0],
                "hedef": en_guvenli[1],
                "kategori": en_guvenli[2],
                "icerik": en_guvenli[3][:200],
                "guven_skoru": en_guvenli[4],
                "basari_sayisi": en_guvenli[5],
                "hata_sayisi": en_guvenli[6],
            }
            kategori = kayit["kategori"]
            kayit_hedef = kayit["hedef"]
            soru = (
                "Hiçbir kayıt tam eşleşmedi ama en güvenilir bildiğim "
                + kategori
                + " kategorisindeki _"
                + kayit_hedef
                + "_.\n\n"
                + "Sanırım **"
                + kayit_hedef
                + "** demek istiyorsun, doğru mu?"
            )
            return {
                "tahmin_kategori": kategori,
                "tahmin_kayit": kayit,
                "guven": 0.01,
                "alternatifler": [],
                "soru": soru,
                "ham_hedef": hedef,
            }

        return {
            "tahmin_kategori": None,
            "tahmin_kayit": None,
            "guven": 0.0,
            "alternatifler": [],
            "soru": None,
            "ham_hedef": hedef,
        }

    # 5) En iyi tahmini seç
    en_iyi_skor, en_iyi_kayit = skorlu[0]

    # Alternatifler (farklı kategorilerden)
    gorulen_kategori: set[str] = set()
    alternatifler = []
    for skor, kayit in skorlu:
        if (
            kayit["kategori"] not in gorulen_kategori
            and len(alternatifler) < max_kategori
        ):
            gorulen_kategori.add(kayit["kategori"])
            alternatifler.append({"skor": round(skor, 2), **kayit})
            if len(alternatifler) >= max_kategori:
                break

    # 6) Soruyu oluştur
    kategori = en_iyi_kayit["kategori"]
    kayit_hedef = en_iyi_kayit["hedef"]
    satir1 = (
        "Hafızamda **"
        + kategori
        + "** kategorisinde _"
        + kayit_hedef
        + "_ bilgisi var."
    )
    soru = satir1 + "\n\nSanırım **" + kayit_hedef + "** demek istiyorsun, doğru mu?"

    return {
        "tahmin_kategori": kategori,
        "tahmin_kayit": en_iyi_kayit,
        "guven": round(en_iyi_skor, 2),
        "alternatifler": alternatifler[1:],
        "soru": soru,
        "ham_hedef": hedef,
    }


def _anahtar_kelimeler(metin: str) -> list[str]:
    """Clean text and split into meaningful keywords."""
    # Türkçe karakterleri normalize et
    temiz = metin.lower().strip()
    # Noktalama işaretlerini kaldır
    for ch in ".,!?;:()[]{}''\"“”‘’…––/":
        temiz = temiz.replace(ch, " ")
    # Kelimelere ayır
    kelimeler = [k for k in temiz.split() if len(k) > 1]
    return kelimeler


def _benzerlik_skoru(
    hedef: str,
    kelimeler: list[str],
    kayit: dict[str, Any],
) -> float:
    """
    Calculate similarity score between two texts.

    3 factors:
    - Keyword match (target vs record.target)
    - Category match (keywords vs record.category)
    - Confidence score bonus
    """
    kayit_kelimeler = _anahtar_kelimeler(kayit["hedef"] + " " + kayit["kategori"])
    if not kayit_kelimeler:
        return 0.0

    # Kelime eşleşme oranı
    eslesen = sum(1 for k in kelimeler if k in kayit_kelimeler)
    toplam = max(len(kelimeler), len(kayit_kelimeler))
    kelime_skor = eslesen / toplam if toplam > 0 else 0.0

    # Kategori eşleşmesi (kategori adındaki kelimeler)
    kat_kelimeler = _anahtar_kelimeler(kayit["kategori"])
    kat_eslesen = sum(1 for k in kelimeler if k in kat_kelimeler)
    kat_skor = kat_eslesen / max(len(kelimeler), 1) * 0.5  # max 0.5 bonus

    # Güven skoru bonusu (guven > 0.8 ise +0.1, guven > 0.5 ise +0.05)
    guven_bonus = 0.0
    if kayit["guven_skoru"] >= 0.8:
        guven_bonus = 0.1
    elif kayit["guven_skoru"] >= 0.5:
        guven_bonus = 0.05

    # Toplam skor [0.0, 1.0]
    skor = kelime_skor * 0.6 + kat_skor + guven_bonus
    return min(skor, 1.0)


# ── İlk kurulum ───────────────────────────────────────────────────────────
_db_kur()
