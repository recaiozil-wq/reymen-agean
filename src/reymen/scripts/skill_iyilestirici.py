# -*- coding: utf-8 -*-
"""
skill_iyilestirici.py â€” ReYMeN Skill Ä°yileÅŸtirme/Optimizasyon Sistemi.

KullanÄ±m desenlerinden yola Ã§Ä±karak skill'leri otomatik iyileÅŸtirir
(tÄ±pkÄ± ReYMeN'in otomatik skill optimizasyonu gibi).

Ã–zellikler:
- skills/ dizinindeki SKILL.md dosyalarÄ±nÄ± tarar
- Hangi skill'lerin kullanÄ±ldÄ±ÄŸÄ±nÄ±, ne sÄ±klÄ±kta ve baÅŸarÄ± oranÄ±nÄ± takip eder
- DÃ¼ÅŸÃ¼k performanslÄ± skill'leri (sÄ±k kullanÄ±lan ama dÃ¼ÅŸÃ¼k baÅŸarÄ±) tespit eder
- Ä°yileÅŸtirme Ã¶nerileri Ã¼retir (Ã¶rnek ekleme, hata dÃ¼zeltme, benzer skill'leri birleÅŸtirme)
- Otomatik iyileÅŸtirme uygulayabilir
- SQLite ile kalÄ±cÄ± depolama: skills/improvements.db

KullanÄ±m:
    from reymen.scripts.skill_iyilestirici import SkillIyilestirici

    si = SkillIyilestirici()
    si.skill_kullanimi_kaydet("skill-adÄ±", basarili=True)
    adaylar = si.iyilestirme_adaylari_bul()
    si.otomatik_iyilestir()
    print(si.rapor_uret())
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "SkillIyilestirici",
    "SkillBilgisi",
    "KullanimKaydi",
    "IyilestirmeOnerisi",
    "IyilestirmeRaporu",
]


# â”€â”€ Proje kÃ¶kÃ¼nÃ¼ bul â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _proje_koku() -> Path:
    """ReYMeN proje kÃ¶kÃ¼nÃ¼ bul (__file__ Ã¼zerinden)."""
    return Path(__file__).resolve().parent.parent.parent.parent


def _skills_dizini() -> Path:
    """skills/ dizin yolunu dÃ¶ndÃ¼r."""
    return _proje_koku() / "skills"


def _db_yolu() -> Path:
    """VeritabanÄ± yolunu dÃ¶ndÃ¼r."""
    return _skills_dizini() / "improvements.db"


# â”€â”€ Veri yapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class SkillBilgisi:
    """Bir SKILL.md dosyasÄ±ndan ayrÄ±ÅŸtÄ±rÄ±lmÄ±ÅŸ bilgi."""

    dosya_yolu: str
    ad: str
    aciklama: str = ""
    kategori: str = ""
    versiyon: str = "1.0.0"
    tetikleyiciler: list[str] = field(default_factory=list)
    etiketler: list[str] = field(default_factory=list)
    bayt_boyutu: int = 0
    son_degisiklik: float = 0.0


@dataclass
class KullanimKaydi:
    """Bir skill'in kullanÄ±m kaydÄ±."""

    skill_adi: str
    kullanim_sayisi: int = 0
    basarili_sayisi: int = 0
    basarisiz_sayisi: int = 0
    basari_orani: float = 0.0
    ortalama_sure: float = 0.0
    son_kullanim: float = 0.0


@dataclass
class IyilestirmeOnerisi:
    """Bir skill iÃ§in iyileÅŸtirme Ã¶nerisi."""

    skill_adi: str
    tur: str  # "ornek_ekle", "hata_duzelt", "birlestir", "versiyon_guncelle", "meta_ekle"
    aciklama: str = ""
    oncelik: int = 5  # 1-10, yÃ¼ksek = acil
    uygulandi: bool = False
    olusturulma: float = 0.0


@dataclass
class IyilestirmeRaporu:
    """Ä°yileÅŸtirme sistemi raporu."""

    taranan_skill: int = 0
    toplam_kullanim: int = 0
    aday_sayisi: int = 0
    iyilestirilen: int = 0
    iyilestirme_adaylari: list[dict] = field(default_factory=list)
    ozet: str = ""


# â”€â”€ VeritabanÄ± yÃ¶netimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class _VT:
    """SQLite veritabanÄ± yÃ¶neticisi (iÃ§ sÄ±nÄ±f)."""

    def __init__(self, db_yolu: Path):
        self._db_yolu = db_yolu
        db_yolu.parent.mkdir(parents=True, exist_ok=True)
        self._init_tablolari()

    def _db(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_yolu))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=3000")
        return conn

    def _init_tablolari(self) -> None:
        with self._db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS skill_bilgisi (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    ad          TEXT UNIQUE NOT NULL,
                    dosya_yolu  TEXT NOT NULL,
                    aciklama    TEXT DEFAULT '',
                    kategori    TEXT DEFAULT '',
                    versiyon    TEXT DEFAULT '1.0.0',
                    tetikleyiciler TEXT DEFAULT '[]',
                    etiketler   TEXT DEFAULT '[]',
                    bayt_boyutu INTEGER DEFAULT 0,
                    son_degisiklik REAL DEFAULT 0.0,
                    son_tarama  REAL DEFAULT 0.0
                );

                CREATE TABLE IF NOT EXISTS kullanim_gecmisi (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_adi   TEXT NOT NULL,
                    basarili    INTEGER NOT NULL DEFAULT 1,
                    sure_ms     REAL DEFAULT 0.0,
                    timestamp   REAL NOT NULL,
                    kaynak      TEXT DEFAULT 'manual',
                    metadata    TEXT DEFAULT '{}'
                );
                CREATE INDEX IF NOT EXISTS idx_kul_skill ON kullanim_gecmisi(skill_adi);
                CREATE INDEX IF NOT EXISTS idx_kul_zaman ON kullanim_gecmisi(timestamp);

                CREATE TABLE IF NOT EXISTS iyilestirme_onerileri (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    skill_adi   TEXT NOT NULL,
                    tur         TEXT NOT NULL,
                    aciklama    TEXT DEFAULT '',
                    oncelik     INTEGER DEFAULT 5,
                    uygulandi   INTEGER DEFAULT 0,
                    olusturulma REAL NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_on_skill ON iyilestirme_onerileri(skill_adi);
                CREATE INDEX IF NOT EXISTS idx_on_uygulandi ON iyilestirme_onerileri(uygulandi);

                CREATE TABLE IF NOT EXISTS iyilestirme_raporlari (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   REAL NOT NULL,
                    rapor_json  TEXT NOT NULL
                );
            """)


# â”€â”€ Skill ayrÄ±ÅŸtÄ±rÄ±cÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class _SkillAyrÄ±stÄ±rÄ±cÄ±:
    """SKILL.md dosyalarÄ±nÄ± ayrÄ±ÅŸtÄ±rÄ±r."""

    @staticmethod
    def YAML_meta_ayristir(icerik: str) -> dict:
        """YAML frontmatter'Ä±nÄ± ayrÄ±ÅŸtÄ±r (--- ... ---)."""
        meta = {}
        match = re.match(r"^---\s*\n(.*?)\n---", icerik, re.DOTALL)
        if not match:
            return meta
        yaml_blok = match.group(1)
        for satir in yaml_blok.strip().split("\n"):
            satir = satir.strip()
            if ":" not in satir:
                continue
            anahtar, _, deger = satir.partition(":")
            anahtar = anahtar.strip().lower()
            deger = deger.strip()
            # Listeler: [a, b, c] veya - a\n - b
            if deger.startswith("["):
                deger = [
                    d.strip().strip("\"'")
                    for d in deger.strip("[]").split(",")
                    if d.strip()
                ]
            elif deger.startswith("- "):
                deger = [
                    d.strip("- ").strip("\"'")
                    for d in yaml_blok.split("\n")
                    if d.strip().startswith("- ")
                ]
            else:
                deger = deger.strip("\"'")
            meta[anahtar] = deger
        return meta

    @staticmethod
    def dosyadan_oku(dosya_yolu: Path) -> SkillBilgisi | None:
        """Bir SKILL.md dosyasÄ±nÄ± oku ve SkillBilgisi dÃ¶ndÃ¼r."""
        try:
            icerik = dosya_yolu.read_text("utf-8", errors="replace")
            meta = _SkillAyrÄ±stÄ±rÄ±cÄ±.YAML_meta_ayristir(icerik)
            ad = meta.get("name") or dosya_yolu.stem
            return SkillBilgisi(
                dosya_yolu=str(dosya_yolu),
                ad=ad,
                aciklama=meta.get("description", ""),
                kategori=meta.get("category", ""),
                versiyon=str(meta.get("version", "1.0.0")),
                tetikleyiciler=meta.get("triggers", meta.get("tetikleyiciler", [])),
                etiketler=meta.get("tags", meta.get("etiketler", [])),
                bayt_boyutu=dosya_yolu.stat().st_size,
                son_degisiklik=dosya_yolu.stat().st_mtime,
            )
        except Exception as e:
            logger.warning("Skill okunamadi: %s â€” %s", dosya_yolu, e)
            return None


# â”€â”€ Ana sÄ±nÄ±f â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class SkillIyilestirici:
    """Skill Ä°yileÅŸtirme/Optimizasyon Sistemi.

    KullanÄ±m desenlerinden yola Ã§Ä±karak skill'leri tarar, izler
    ve otomatik iyileÅŸtirir.
    """

    def __init__(self, skills_dizini: str | Path | None = None):
        self._skills_dizini = Path(skills_dizini) if skills_dizini else _skills_dizini()
        self._vt = _VT(_db_yolu())
        self._ayristirici = _SkillAyrÄ±stÄ±rÄ±cÄ±()

    # â”€â”€ Genel tarama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def skill_dosyalarini_tara(self) -> list[SkillBilgisi]:
        """skills/ dizinindeki tÃ¼m SKILL.md dosyalarÄ±nÄ± tara.

        Returns:
            Tarama sonucu SkillBilgisi listesi.
        """
        sonuclar = []
        skills_dir = self._skills_dizini
        if not skills_dir.exists():
            logger.warning("skills/ dizini bulunamadi: %s", skills_dir)
            return sonuclar

        for dosya in sorted(skills_dir.glob("*.md")):
            bilgi = self._ayristirici.dosyadan_oku(dosya)
            if bilgi:
                sonuclar.append(bilgi)
                self._skill_bilgisini_kaydet(bilgi)

        logger.info("%d skill dosyasi tarandi", len(sonuclar))
        return sonuclar

    # â”€â”€ KullanÄ±m kaydÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def skill_kullanimi_kaydet(
        self,
        skill_adi: str,
        basarili: bool,
        sure_ms: float = 0.0,
        kaynak: str = "manual",
        metadata: dict | None = None,
    ) -> None:
        """Bir skill kullanÄ±mÄ±nÄ± kaydet.

        Args:
            skill_adi: Skill adÄ±.
            basarili: KullanÄ±m baÅŸarÄ±lÄ± mÄ±?
            sure_ms: Ä°ÅŸlem sÃ¼resi (milisaniye).
            kaynak: KullanÄ±m kaynaÄŸÄ± (manual, otomatik, cron vb.).
            metadata: Ek bilgiler.
        """
        with self._vt._db() as db:
            db.execute(
                """INSERT INTO kullanim_gecmisi
                   (skill_adi, basarili, sure_ms, timestamp, kaynak, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    skill_adi,
                    1 if basarili else 0,
                    sure_ms,
                    time.time(),
                    kaynak,
                    json.dumps(metadata or {}),
                ),
            )
        logger.debug(
            "Kullanim kaydedildi: %s â€” %s (%s)",
            skill_adi,
            "basarili" if basarili else "basarisiz",
            kaynak,
        )

    def skill_istatistikleri(self, skill_adi: str) -> KullanimKaydi:
        """Bir skill'in istatistiklerini dÃ¶ndÃ¼r."""
        with self._vt._db() as db:
            row = db.execute(
                """SELECT
                    COUNT(*) as kullanim,
                    SUM(basarili) as basarili,
                    COUNT(*) - SUM(basarili) as basarisiz,
                    CASE WHEN COUNT(*) > 0
                        THEN ROUND(CAST(SUM(basarili) AS REAL) / COUNT(*) * 100, 1)
                        ELSE 0.0
                    END as basari_orani,
                    COALESCE(AVG(sure_ms), 0.0) as ortalama_sure,
                    COALESCE(MAX(timestamp), 0.0) as son_kullanim
                   FROM kullanim_gecmisi
                   WHERE skill_adi = ?""",
                (skill_adi,),
            ).fetchone()
            if row and row["kullanim"] > 0:
                return KullanimKaydi(
                    skill_adi=skill_adi,
                    kullanim_sayisi=row["kullanim"],
                    basarili_sayisi=row["basarili"],
                    basarisiz_sayisi=row["basarisiz"],
                    basari_orani=row["basari_orani"],
                    ortalama_sure=row["ortalama_sure"],
                    son_kullanim=row["son_kullanim"],
                )
        return KullanimKaydi(skill_adi=skill_adi)

    # â”€â”€ Ä°yileÅŸtirme adaylarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def iyilestirme_adaylari_bul(self) -> list[dict]:
        """Ä°yileÅŸtirilmesi gereken skill'leri tespit et.

        Kriterler:
            1. **DÃ¼ÅŸÃ¼k baÅŸarÄ± oranÄ±**: >= 5 kullanÄ±m ve baÅŸarÄ± oranÄ± < %60
            2. **SÄ±k kullanÄ±lan ama dÃ¼ÅŸÃ¼k baÅŸarÄ±**: >= 20 kullanÄ±m ve baÅŸarÄ± oranÄ± < %70
            3. **Eksik metadata**: YAML frontmatter'Ä± eksik skill'ler
            4. **Benzer skill'ler**: AynÄ± kategori/etiket paylaÅŸan ve birleÅŸtirilebilecek skill'ler
            5. **GÃ¼ncellenmemiÅŸ skill**: 30 gÃ¼nden eski ve hiÃ§ kullanÄ±lmamÄ±ÅŸ

        Returns:
            Ä°yileÅŸtirme adayÄ± skill listesi (her biri dict).
        """
        adaylar = []
        skills_dir = self._skills_dizini

        # TÃ¼m skill'leri tara
        tum_skilller = self.skill_dosyalarini_tara()
        skill_istatistik = {}

        for s in tum_skilller:
            istatistik = self.skill_istatistikleri(s.ad)
            skill_istatistik[s.ad] = istatistik

            # Kriter 1: DÃ¼ÅŸÃ¼k baÅŸarÄ± oranÄ±
            if istatistik.kullanim_sayisi >= 5 and istatistik.basari_orani < 60.0:
                adaylar.append(
                    {
                        "skill_adi": s.ad,
                        "tur": "dusuk_basari",
                        "aciklama": (
                            f"BaÅŸarÄ± oranÄ± dÃ¼ÅŸÃ¼k: %{istatistik.basari_orani:.1f} "
                            f"({istatistik.basarili_sayisi}/{istatistik.kullanim_sayisi} baÅŸarÄ±lÄ±) â€” "
                            f"hata senaryolarÄ± ve Ã¶rnekler eklenmeli"
                        ),
                        "oncelik": 9,
                        "veri": {
                            "kullanim": istatistik.kullanim_sayisi,
                            "basarili": istatistik.basarili_sayisi,
                            "basari_orani": istatistik.basari_orani,
                        },
                    }
                )

            # Kriter 2: SÄ±k kullanÄ±lan ama dÃ¼ÅŸÃ¼k baÅŸarÄ±
            elif istatistik.kullanim_sayisi >= 20 and istatistik.basari_orani < 70.0:
                adaylar.append(
                    {
                        "skill_adi": s.ad,
                        "tur": "sik_kullanilan_dusuk_basari",
                        "aciklama": (
                            f"SÄ±k kullanÄ±lÄ±yor ({istatistik.kullanim_sayisi} kez) ama "
                            f"baÅŸarÄ± oranÄ± dÃ¼ÅŸÃ¼k: %{istatistik.basari_orani:.1f} â€” "
                            f"pitfall'lar dÃ¼zeltilmeli, daha net talimatlar eklenmeli"
                        ),
                        "oncelik": 8,
                        "veri": {
                            "kullanim": istatistik.kullanim_sayisi,
                            "basarili": istatistik.basarili_sayisi,
                            "basari_orani": istatistik.basari_orani,
                        },
                    }
                )

            # Kriter 3: Eksik metadata
            eksik = self._eksik_meta_kontrol(s)
            if eksik:
                adaylar.append(
                    {
                        "skill_adi": s.ad,
                        "tur": "eksik_meta",
                        "aciklama": f"Eksik metadata: {', '.join(eksik)}",
                        "oncelik": 6,
                        "veri": {"eksik_alanlar": eksik},
                    }
                )

        # Kriter 4: Benzer skill'ler (kategori bazlÄ± gruplama)
        for s1 in tum_skilller:
            for s2 in tum_skilller:
                if s1.ad >= s2.ad:
                    continue
                benzerlik = self._benzerlik_skoru(s1, s2)
                if benzerlik >= 0.6:
                    adaylar.append(
                        {
                            "skill_adi": f"{s1.ad} + {s2.ad}",
                            "tur": "birlestir",
                            "aciklama": (
                                f"'{s1.ad}' ve '{s2.ad}' benzer (benzerlik: %{benzerlik:.0f}) â€” "
                                f"tek bir skill'de birleÅŸtirilebilir"
                            ),
                            "oncelik": 4,
                            "veri": {
                                "skill1": s1.ad,
                                "skill2": s2.ad,
                                "benzerlik": round(benzerlik, 2),
                            },
                        }
                    )

        # Kriter 5: GÃ¼ncellenmemiÅŸ / hiÃ§ kullanÄ±lmamÄ±ÅŸ skill
        simdi = time.time()
        for s in tum_skilller:
            istatistik = skill_istatistik.get(s.ad, KullanimKaydi(skill_adi=s.ad))
            if (
                istatistik.kullanim_sayisi == 0
                and (simdi - s.son_degisiklik) > 30 * 86400
            ):
                adaylar.append(
                    {
                        "skill_adi": s.ad,
                        "tur": "kullanilmayan",
                        "aciklama": (
                            f"30 gÃ¼nden eski ({int((simdi - s.son_degisiklik) / 86400)} gÃ¼n) "
                            f"ve hiÃ§ kullanÄ±lmamÄ±ÅŸ â€” gÃ¶zden geÃ§irilmeli veya kaldÄ±rÄ±lmalÄ±"
                        ),
                        "oncelik": 3,
                        "veri": {
                            "gun_oncesi": int((simdi - s.son_degisiklik) / 86400),
                        },
                    }
                )

        # Ã–nerileri veritabanÄ±na kaydet
        self._oneri_kaydet(adaylar)
        logger.info("%d iyilestirme adayi bulundu", len(adaylar))
        return adaylar

    # â”€â”€ Otomatik iyileÅŸtirme â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def otomatik_iyilestir(self) -> int:
        """Ä°yileÅŸtirme adaylarÄ±na otomatik dÃ¼zeltmeler uygula.

        YapÄ±lanlar:
        - Eksik metadata varsa YAML frontmatter'Ä±nÄ± ekler
        - Benzer skill'ler iÃ§in birleÅŸtirme notu ekler
        - DÃ¼ÅŸÃ¼k baÅŸarÄ±lÄ± skill'lere hata senaryosu bÃ¶lÃ¼mÃ¼ ekler

        Returns:
            Ä°yileÅŸtirilen skill sayÄ±sÄ±.
        """
        adaylar = self.iyilestirme_adaylari_bul()
        iyilestirilen = 0

        for aday in adaylar:
            tur = aday["tur"]
            skill_adi = aday["skill_adi"]

            if tur == "eksik_meta":
                if self._meta_iyilestir(skill_adi):
                    iyilestirilen += 1

            elif tur in ("dusuk_basari", "sik_kullanilan_dusuk_basari"):
                if self._hata_senaryosu_ekle(skill_adi, aday["veri"]):
                    iyilestirilen += 1

            elif tur == "kullanilmayan":
                if self._kullanilmayan_notu_ekle(skill_adi):
                    iyilestirilen += 1

        # Ä°yileÅŸtirmeleri uygulandÄ± olarak iÅŸaretle
        with self._vt._db() as db:
            db.execute(
                "UPDATE iyilestirme_onerileri SET uygulandi = 1 WHERE uygulandi = 0"
            )

        logger.info("%d skill iyilestirildi", iyilestirilen)
        return iyilestirilen

    # â”€â”€ Rapor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def rapor_uret(self) -> str:
        """KapsamlÄ± iyileÅŸtirme raporu Ã¼ret.

        Returns:
            Ä°nsan tarafÄ±ndan okunabilir rapor metni.
        """
        # TÃ¼m skill'leri tara
        tum_skilller = self.skill_dosyalarini_tara()
        toplam_kullanim = 0
        basarili_toplam = 0
        skill_detaylari = []

        for s in tum_skilller:
            istatistik = self.skill_istatistikleri(s.ad)
            toplam_kullanim += istatistik.kullanim_sayisi
            basarili_toplam += istatistik.basarili_sayisi
            skill_detaylari.append(
                {
                    "ad": s.ad,
                    "kategori": s.kategori,
                    "versiyon": s.versiyon,
                    "kullanim": istatistik.kullanim_sayisi,
                    "basari_orani": istatistik.basari_orani,
                    "ortalama_sure_ms": round(istatistik.ortalama_sure, 1),
                }
            )

        # Ä°yileÅŸtirme adaylarÄ±
        adaylar = self.iyilestirme_adaylari_bul()
        uygulanan = 0
        with self._vt._db() as db:
            row = db.execute(
                "SELECT COUNT(*) as sayi FROM iyilestirme_onerileri WHERE uygulandi = 1"
            ).fetchone()
            uygulanan = row["sayi"] if row else 0

        # Genel baÅŸarÄ± oranÄ±
        genel_basari = 0.0
        if toplam_kullanim > 0:
            genel_basari = round(basarili_toplam / toplam_kullanim * 100, 1)

        # Rapor metni
        satirlar = [
            "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—",
            "â•‘     ğŸ”§ SKILL Ä°YÄ°LEÅTÄ°RME RAPORU                        â•‘",
            "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•",
            "",
            f"Tarih: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "â”€â”€ GENEL DURUM â”€â”€",
            f"  Taranan skill      : {len(tum_skilller)}",
            f"  Toplam kullanÄ±m    : {toplam_kullanim}",
            f"  Genel baÅŸarÄ± oranÄ± : %{genel_basari}",
            f"  Ä°yileÅŸtirme adayÄ±  : {len(adaylar)}",
            f"  Uygulanan iyileÅŸt. : {uygulanan}",
            "",
            "â”€â”€ SKILL DETAYLARI â”€â”€",
        ]

        # Skill detaylarÄ±nÄ± sÄ±rala (en Ã§ok kullanÄ±lan -> en az)
        skill_detaylari.sort(key=lambda x: x["kullanim"], reverse=True)
        for sd in skill_detaylari[:20]:  # Ä°lk 20
            basari_gostergesi = (
                "âœ…"
                if sd["basari_orani"] >= 70
                else ("âš ï¸" if sd["basari_orani"] >= 40 else "âŒ")
            )
            satirlar.append(
                f"  {basari_gostergesi} {sd['ad']} "
                f"(v{sd['versiyon']}, {sd['kategori'] or 'kategorisiz'})"
            )
            satirlar.append(
                f"     KullanÄ±m: {sd['kullanim']} kez, "
                f"BaÅŸarÄ±: %{sd['basari_orani']}, "
                f"SÃ¼re: {sd['ortalama_sure_ms']}ms"
            )

        if adaylar:
            satirlar.extend(
                [
                    "",
                    "â”€â”€ Ä°YÄ°LEÅTÄ°RME Ã–NERÄ°LERÄ° â”€â”€",
                ]
            )
            # Ã–nceliÄŸe gÃ¶re sÄ±rala
            adaylar.sort(key=lambda x: x["oncelik"], reverse=True)
            for i, aday in enumerate(adaylar[:10], 1):  # Ä°lk 10
                tur_ikonlari = {
                    "dusuk_basari": "ğŸ”´",
                    "sik_kullanilan_dusuk_basari": "ğŸŸ ",
                    "eksik_meta": "ğŸŸ¡",
                    "birlestir": "ğŸ”µ",
                    "kullanilmayan": "âšª",
                }
                ikon = tur_ikonlari.get(aday["tur"], "âš«")
                satirlar.append(
                    f"  {i}. {ikon} [{aday['tur'].upper()}] {aday['skill_adi']}"
                )
                satirlar.append(f"     Ã–ncelik: {aday['oncelik']}/10")
                satirlar.append(f"     {aday['aciklama']}")
        else:
            satirlar.extend(
                [
                    "",
                    "â”€â”€ Ä°YÄ°LEÅTÄ°RME Ã–NERÄ°LERÄ° â”€â”€",
                    "  âœ… TÃ¼m skill'ler iyi durumda. Ä°yileÅŸtirme gerekmiyor.",
                ]
            )

        satirlar.extend(
            [
                "",
                "â”€â”€ SON Ä°ÅLEMLER â”€â”€",
                f"  Son otomatik iyileÅŸtirmede {uygulanan} skill gÃ¼ncellendi.",
                "",
            ]
        )

        # Raporu veritabanÄ±na kaydet
        rapor_metni = "\n".join(satirlar)
        with self._vt._db() as db:
            db.execute(
                "INSERT INTO iyilestirme_raporlari (timestamp, rapor_json) VALUES (?, ?)",
                (
                    time.time(),
                    json.dumps(
                        {"rapor": rapor_metni, "tarih": str(datetime.now(timezone.utc))}
                    ),
                ),
            )

        return rapor_metni

    # â”€â”€ Ä°Ã§ yardÄ±mcÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _skill_bilgisini_kaydet(self, bilgi: SkillBilgisi) -> None:
        """Skill bilgisini veritabanÄ±na kaydet/gÃ¼ncelle."""
        with self._vt._db() as db:
            db.execute(
                """INSERT OR REPLACE INTO skill_bilgisi
                   (ad, dosya_yolu, aciklama, kategori, versiyon,
                    tetikleyiciler, etiketler, bayt_boyutu,
                    son_degisiklik, son_tarama)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    bilgi.ad,
                    bilgi.dosya_yolu,
                    bilgi.aciklama,
                    bilgi.kategori,
                    bilgi.versiyon,
                    json.dumps(bilgi.tetikleyiciler),
                    json.dumps(bilgi.etiketler),
                    bilgi.bayt_boyutu,
                    bilgi.son_degisiklik,
                    time.time(),
                ),
            )

    def _eksik_meta_kontrol(self, bilgi: SkillBilgisi) -> list[str]:
        """Skill'de eksik metadata alanlarÄ±nÄ± bul."""
        eksik = []
        if not bilgi.aciklama:
            eksik.append("description/aÃ§Ä±klama")
        if not bilgi.kategori:
            eksik.append("category/kategori")
        if not bilgi.tetikleyiciler:
            eksik.append("triggers/tetikleyiciler")
        return eksik

    def _benzerlik_skoru(self, s1: SkillBilgisi, s2: SkillBilgisi) -> float:
        """Ä°ki skill arasÄ±ndaki benzerlik skoru (0.0-1.0)."""
        puan = 0.0
        toplam = 0.0

        # Kategori benzerliÄŸi
        toplam += 1.0
        if s1.kategori and s2.kategori and s1.kategori.lower() == s2.kategori.lower():
            puan += 1.0

        # Etiket benzerliÄŸi
        if s1.etiketler and s2.etiketler:
            s1_set = set(t.lower() for t in s1.etiketler)
            s2_set = set(t.lower() for t in s2.etiketler)
            toplam += 1.0
            if s1_set & s2_set:
                puan += len(s1_set & s2_set) / max(len(s1_set | s2_set), 1)

        # Tetikleyici benzerliÄŸi
        if s1.tetikleyiciler and s2.tetikleyiciler:
            s1_set = set(t.lower() for t in s1.tetikleyiciler)
            s2_set = set(t.lower() for t in s2.tetikleyiciler)
            toplam += 1.0
            if s1_set & s2_set:
                puan += len(s1_set & s2_set) / max(len(s1_set | s2_set), 1)

        # Ä°sim benzerliÄŸi (anahtar kelime ortaklÄ±ÄŸÄ±)
        if s1.ad and s2.ad:
            s1_kelime = set(s1.ad.lower().replace("-", " ").replace("_", " ").split())
            s2_kelime = set(s2.ad.lower().replace("-", " ").replace("_", " ").split())
            toplam += 1.0
            if s1_kelime & s2_kelime:
                puan += len(s1_kelime & s2_kelime) / max(len(s1_kelime | s2_kelime), 1)

        return puan / max(toplam, 1)

    def _oneri_kaydet(self, adaylar: list[dict]) -> None:
        """Ä°yileÅŸtirme Ã¶nerilerini veritabanÄ±na kaydet."""
        simdi = time.time()
        with self._vt._db() as db:
            for aday in adaylar:
                db.execute(
                    """INSERT OR IGNORE INTO iyilestirme_onerileri
                       (skill_adi, tur, aciklama, oncelik, uygulandi, olusturulma)
                       VALUES (?, ?, ?, ?, 0, ?)""",
                    (
                        aday["skill_adi"],
                        aday["tur"],
                        aday["aciklama"],
                        aday["oncelik"],
                        simdi,
                    ),
                )

    def _meta_iyilestir(self, skill_adi: str) -> bool:
        """Skill'e eksik YAML metadata ekle."""
        try:
            # Skill dosyasÄ±nÄ± bul
            skills_dir = self._skills_dizini
            for dosya in skills_dir.glob("*.md"):
                bilgi = self._ayristirici.dosyadan_oku(dosya)
                if bilgi and bilgi.ad == skill_adi:
                    icerik = dosya.read_text("utf-8", errors="replace")
                    meta = _SkillAyrÄ±stÄ±rÄ±cÄ±.YAML_meta_ayristir(icerik)

                    # Eksik alanlarÄ± tespit et
                    eklenecek = []
                    if not meta.get("name"):
                        eklenecek.append(f"name: {bilgi.ad}")
                    if not meta.get("description"):
                        eklenecek.append(f"description: {bilgi.ad} skill'i")
                    if not meta.get("category"):
                        eklenecek.append("category: genel")
                    if not meta.get("version"):
                        eklenecek.append("version: 1.0.0")

                    if not eklenecek:
                        return False

                    # Var olan YAML frontmatter'Ä±na ekle veya yeni oluÅŸtur
                    if re.match(r"^---\s*\n.*?\n---", icerik, re.DOTALL):
                        # Mevcut frontmatter'Ä± gÃ¼ncelle
                        def _ekle_meta(m):
                            blok = m.group(0)
                            # Son ---'den Ã¶nce ekle
                            ek = "\n".join(eklenecek)
                            return blok.rstrip("---\n") + "\n" + ek + "\n---"

                        yeni_icerik = re.sub(
                            r"^---\s*\n.*?\n---",
                            _ekle_meta,
                            icerik,
                            count=1,
                            flags=re.DOTALL,
                        )
                    else:
                        # Yeni frontmatter oluÅŸtur
                        yeni_meta = "---\n" + "\n".join(eklenecek) + "\n---\n\n"
                        yeni_icerik = yeni_meta + icerik

                    dosya.write_text(yeni_icerik, encoding="utf-8")
                    logger.info(
                        "Meta iyilestirildi: %s (%s)", skill_adi, ", ".join(eklenecek)
                    )
                    return True
        except Exception as e:
            logger.warning("Meta iyilestirme hatasi: %s â€” %s", skill_adi, e)
        return False

    def _hata_senaryosu_ekle(self, skill_adi: str, veri: dict) -> bool:
        """DÃ¼ÅŸÃ¼k baÅŸarÄ±lÄ± skill'e hata senaryosu bÃ¶lÃ¼mÃ¼ ekle."""
        try:
            skills_dir = self._skills_dizini
            for dosya in skills_dir.glob("*.md"):
                bilgi = self._ayristirici.dosyadan_oku(dosya)
                if bilgi and bilgi.ad == skill_adi:
                    icerik = dosya.read_text("utf-8", errors="replace")

                    # Zaten hata senaryosu var mÄ±?
                    if "## Hata SenaryolarÄ±" in icerik or "## Pitfall" in icerik:
                        return False

                    # BaÅŸarÄ± oranÄ± bilgisi
                    basari = veri.get("basari_orani", 0)
                    kullanim = veri.get("kullanim", 0)

                    hata_bloku = (
                        "\n\n"
                        "## âš ï¸ Hata SenaryolarÄ±\n"
                        "\n"
                        f"> Bu skill %{basari:.1f} baÅŸarÄ± oranÄ±na sahip "
                        f"({kullanim} kullanÄ±m). AÅŸaÄŸÄ±daki hata senaryolarÄ± gÃ¶zden geÃ§irilmeli.\n"
                        "\n"
                        "### Bilinen Hatalar\n"
                        "- **Hata 1**: AÃ§Ä±klama eklenmeli\n"
                        "- **Hata 2**: AÃ§Ä±klama eklenmeli\n"
                        "\n"
                        "### Ã‡Ã¶zÃ¼m Ã–nerileri\n"
                        "- KullanÄ±m talimatlarÄ± netleÅŸtirilmeli\n"
                        "- Beklenen Ã§Ä±ktÄ± formatÄ± belirtilmeli\n"
                        "- SÄ±nÄ±r durumlar (edge cases) belgelenmeli\n"
                    )

                    yeni_icerik = icerik.rstrip() + hata_bloku
                    dosya.write_text(yeni_icerik, encoding="utf-8")
                    logger.info(
                        "Hata senaryosu eklendi: %s (basari: %%%.1f, kullanim: %d)",
                        skill_adi,
                        basari,
                        kullanim,
                    )
                    return True
        except Exception as e:
            logger.warning("Hata senaryosu ekleme hatasi: %s â€” %s", skill_adi, e)
        return False

    def _kullanilmayan_notu_ekle(self, skill_adi: str) -> bool:
        """KullanÄ±lmayan skill'e gÃ¶zden geÃ§irme notu ekle."""
        try:
            skills_dir = self._skills_dizini
            for dosya in skills_dir.glob("*.md"):
                bilgi = self._ayristirici.dosyadan_oku(dosya)
                if bilgi and bilgi.ad == skill_adi:
                    icerik = dosya.read_text("utf-8", errors="replace")

                    if "---\n# GÃ–ZDEN GEÃ‡Ä°R" in icerik or "---\n# REVIEW" in icerik:
                        return False

                    not_bloku = (
                        "\n\n"
                        "---\n"
                        "# GÃ–ZDEN GEÃ‡Ä°R\n"
                        "\n"
                        "> â° Bu skill 30 gÃ¼nden uzun sÃ¼redir gÃ¼ncellenmemiÅŸ "
                        "ve hiÃ§ kullanÄ±lmamÄ±ÅŸ. KaldÄ±rÄ±labilir veya gÃ¼ncellenebilir.\n"
                    )

                    yeni_icerik = icerik.rstrip() + not_bloku
                    dosya.write_text(yeni_icerik, encoding="utf-8")
                    logger.info("Kullanilmayan notu eklendi: %s", skill_adi)
                    return True
        except Exception as e:
            logger.warning("Kullanilmayan notu ekleme hatasi: %s â€” %s", skill_adi, e)
        return False

    # â”€â”€ Ek yardÄ±mcÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def en_cok_kullanilan_skilller(self, limit: int = 10) -> list[dict]:
        """En Ã§ok kullanÄ±lan skill'leri dÃ¶ndÃ¼r."""
        with self._vt._db() as db:
            rows = db.execute(
                """SELECT skill_adi, COUNT(*) as sayi,
                          SUM(basarili) as basarili,
                          ROUND(CAST(SUM(basarili) AS REAL) / COUNT(*) * 100, 1) as basari_orani
                   FROM kullanim_gecmisi
                   GROUP BY skill_adi
                   ORDER BY sayi DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def son_kullanimlar(self, limit: int = 20) -> list[dict]:
        """Son kullanÄ±mlarÄ± dÃ¶ndÃ¼r."""
        with self._vt._db() as db:
            rows = db.execute(
                """SELECT skill_adi, basarili, sure_ms, timestamp, kaynak
                   FROM kullanim_gecmisi
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def istatistik_sifirla(self, skill_adi: str | None = None) -> None:
        """Skill kullanÄ±m istatistiklerini sÄ±fÄ±rla."""
        with self._vt._db() as db:
            if skill_adi:
                db.execute(
                    "DELETE FROM kullanim_gecmisi WHERE skill_adi = ?", (skill_adi,)
                )
            else:
                db.execute("DELETE FROM kullanim_gecmisi")
            logger.info(
                "Istatistikler sifirlandi%s",
                f" â€” {skill_adi}" if skill_adi else " (tum skill'ler)",
            )


# â”€â”€ CLI kullanÄ±mÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def main() -> str:
    """CLI giriÅŸ noktasÄ±.

    KullanÄ±m:
        python -m reymen.scripts.skill_iyilestirici
    """
    si = SkillIyilestirici()

    # 1. Skill'leri tara
    print("ğŸ“‚ Skill'ler taranÄ±yor...")
    skill_sayisi = len(si.skill_dosyalarini_tara())
    print(f"   {skill_sayisi} skill bulundu")

    # 2. Ä°yileÅŸtirme adaylarÄ±nÄ± bul
    print("\nğŸ” Ä°yileÅŸtirme adaylarÄ± taranÄ±yor...")
    adaylar = si.iyilestirme_adaylari_bul()
    print(f"   {len(adaylar)} aday bulundu")

    # 3. Otomatik iyileÅŸtir
    if adaylar:
        print("\nğŸ› ï¸  Otomatik iyileÅŸtirme uygulanÄ±yor...")
        iyilestirilen = si.otomatik_iyilestir()
        print(f"   {iyilestirilen} skill iyileÅŸtirildi")
    else:
        print("\nâœ… Ä°yileÅŸtirme gerekmiyor")
        iyilestirilen = 0

    # 4. Rapor Ã¼ret
    print("\nğŸ“Š Rapor Ã¼retiliyor...")
    rapor = si.rapor_uret()
    print(rapor)

    return rapor


if __name__ == "__main__":
    main()
