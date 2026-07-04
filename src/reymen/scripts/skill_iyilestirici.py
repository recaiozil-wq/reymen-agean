# -*- coding: utf-8 -*-
"""
skill_iyilestirici.py — ReYMeN Skill İyileştirme/Optimizasyon Sistemi.

Kullanım desenlerinden yola çıkarak skill'leri otomatik iyileştirir
(tıpkı Hermes'in otomatik skill optimizasyonu gibi).

Özellikler:
- skills/ dizinindeki SKILL.md dosyalarını tarar
- Hangi skill'lerin kullanıldığını, ne sıklıkta ve başarı oranını takip eder
- Düşük performanslı skill'leri (sık kullanılan ama düşük başarı) tespit eder
- İyileştirme önerileri üretir (örnek ekleme, hata düzeltme, benzer skill'leri birleştirme)
- Otomatik iyileştirme uygulayabilir
- SQLite ile kalıcı depolama: skills/improvements.db

Kullanım:
    from reymen.scripts.skill_iyilestirici import SkillIyilestirici

    si = SkillIyilestirici()
    si.skill_kullanimi_kaydet("skill-adı", basarili=True)
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


# ── Proje kökünü bul ───────────────────────────────────────────────


def _proje_koku() -> Path:
    """ReYMeN proje kökünü bul (__file__ üzerinden)."""
    return Path(__file__).resolve().parent.parent.parent.parent


def _skills_dizini() -> Path:
    """skills/ dizin yolunu döndür."""
    return _proje_koku() / "skills"


def _db_yolu() -> Path:
    """Veritabanı yolunu döndür."""
    return _skills_dizini() / "improvements.db"


# ── Veri yapıları ──────────────────────────────────────────────────


@dataclass
class SkillBilgisi:
    """Bir SKILL.md dosyasından ayrıştırılmış bilgi."""

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
    """Bir skill'in kullanım kaydı."""

    skill_adi: str
    kullanim_sayisi: int = 0
    basarili_sayisi: int = 0
    basarisiz_sayisi: int = 0
    basari_orani: float = 0.0
    ortalama_sure: float = 0.0
    son_kullanim: float = 0.0


@dataclass
class IyilestirmeOnerisi:
    """Bir skill için iyileştirme önerisi."""

    skill_adi: str
    tur: str  # "ornek_ekle", "hata_duzelt", "birlestir", "versiyon_guncelle", "meta_ekle"
    aciklama: str = ""
    oncelik: int = 5  # 1-10, yüksek = acil
    uygulandi: bool = False
    olusturulma: float = 0.0


@dataclass
class IyilestirmeRaporu:
    """İyileştirme sistemi raporu."""

    taranan_skill: int = 0
    toplam_kullanim: int = 0
    aday_sayisi: int = 0
    iyilestirilen: int = 0
    iyilestirme_adaylari: list[dict] = field(default_factory=list)
    ozet: str = ""


# ── Veritabanı yönetimi ────────────────────────────────────────────


class _VT:
    """SQLite veritabanı yöneticisi (iç sınıf)."""

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


# ── Skill ayrıştırıcı ──────────────────────────────────────────────


class _SkillAyrıstırıcı:
    """SKILL.md dosyalarını ayrıştırır."""

    @staticmethod
    def YAML_meta_ayristir(icerik: str) -> dict:
        """YAML frontmatter'ını ayrıştır (--- ... ---)."""
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
        """Bir SKILL.md dosyasını oku ve SkillBilgisi döndür."""
        try:
            icerik = dosya_yolu.read_text("utf-8", errors="replace")
            meta = _SkillAyrıstırıcı.YAML_meta_ayristir(icerik)
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
            logger.warning("Skill okunamadi: %s — %s", dosya_yolu, e)
            return None


# ── Ana sınıf ──────────────────────────────────────────────────────


class SkillIyilestirici:
    """Skill İyileştirme/Optimizasyon Sistemi.

    Kullanım desenlerinden yola çıkarak skill'leri tarar, izler
    ve otomatik iyileştirir.
    """

    def __init__(self, skills_dizini: str | Path | None = None):
        self._skills_dizini = Path(skills_dizini) if skills_dizini else _skills_dizini()
        self._vt = _VT(_db_yolu())
        self._ayristirici = _SkillAyrıstırıcı()

    # ── Genel tarama ───────────────────────────────────────────────

    def skill_dosyalarini_tara(self) -> list[SkillBilgisi]:
        """skills/ dizinindeki tüm SKILL.md dosyalarını tara.

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

    # ── Kullanım kaydı ─────────────────────────────────────────────

    def skill_kullanimi_kaydet(
        self,
        skill_adi: str,
        basarili: bool,
        sure_ms: float = 0.0,
        kaynak: str = "manual",
        metadata: dict | None = None,
    ) -> None:
        """Bir skill kullanımını kaydet.

        Args:
            skill_adi: Skill adı.
            basarili: Kullanım başarılı mı?
            sure_ms: İşlem süresi (milisaniye).
            kaynak: Kullanım kaynağı (manual, otomatik, cron vb.).
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
            "Kullanim kaydedildi: %s — %s (%s)",
            skill_adi,
            "basarili" if basarili else "basarisiz",
            kaynak,
        )

    def skill_istatistikleri(self, skill_adi: str) -> KullanimKaydi:
        """Bir skill'in istatistiklerini döndür."""
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

    # ── İyileştirme adayları ───────────────────────────────────────

    def iyilestirme_adaylari_bul(self) -> list[dict]:
        """İyileştirilmesi gereken skill'leri tespit et.

        Kriterler:
            1. **Düşük başarı oranı**: >= 5 kullanım ve başarı oranı < %60
            2. **Sık kullanılan ama düşük başarı**: >= 20 kullanım ve başarı oranı < %70
            3. **Eksik metadata**: YAML frontmatter'ı eksik skill'ler
            4. **Benzer skill'ler**: Aynı kategori/etiket paylaşan ve birleştirilebilecek skill'ler
            5. **Güncellenmemiş skill**: 30 günden eski ve hiç kullanılmamış

        Returns:
            İyileştirme adayı skill listesi (her biri dict).
        """
        adaylar = []
        skills_dir = self._skills_dizini

        # Tüm skill'leri tara
        tum_skilller = self.skill_dosyalarini_tara()
        skill_istatistik = {}

        for s in tum_skilller:
            istatistik = self.skill_istatistikleri(s.ad)
            skill_istatistik[s.ad] = istatistik

            # Kriter 1: Düşük başarı oranı
            if istatistik.kullanim_sayisi >= 5 and istatistik.basari_orani < 60.0:
                adaylar.append(
                    {
                        "skill_adi": s.ad,
                        "tur": "dusuk_basari",
                        "aciklama": (
                            f"Başarı oranı düşük: %{istatistik.basari_orani:.1f} "
                            f"({istatistik.basarili_sayisi}/{istatistik.kullanim_sayisi} başarılı) — "
                            f"hata senaryoları ve örnekler eklenmeli"
                        ),
                        "oncelik": 9,
                        "veri": {
                            "kullanim": istatistik.kullanim_sayisi,
                            "basarili": istatistik.basarili_sayisi,
                            "basari_orani": istatistik.basari_orani,
                        },
                    }
                )

            # Kriter 2: Sık kullanılan ama düşük başarı
            elif istatistik.kullanim_sayisi >= 20 and istatistik.basari_orani < 70.0:
                adaylar.append(
                    {
                        "skill_adi": s.ad,
                        "tur": "sik_kullanilan_dusuk_basari",
                        "aciklama": (
                            f"Sık kullanılıyor ({istatistik.kullanim_sayisi} kez) ama "
                            f"başarı oranı düşük: %{istatistik.basari_orani:.1f} — "
                            f"pitfall'lar düzeltilmeli, daha net talimatlar eklenmeli"
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

        # Kriter 4: Benzer skill'ler (kategori bazlı gruplama)
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
                                f"'{s1.ad}' ve '{s2.ad}' benzer (benzerlik: %{benzerlik:.0f}) — "
                                f"tek bir skill'de birleştirilebilir"
                            ),
                            "oncelik": 4,
                            "veri": {
                                "skill1": s1.ad,
                                "skill2": s2.ad,
                                "benzerlik": round(benzerlik, 2),
                            },
                        }
                    )

        # Kriter 5: Güncellenmemiş / hiç kullanılmamış skill
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
                            f"30 günden eski ({int((simdi - s.son_degisiklik) / 86400)} gün) "
                            f"ve hiç kullanılmamış — gözden geçirilmeli veya kaldırılmalı"
                        ),
                        "oncelik": 3,
                        "veri": {
                            "gun_oncesi": int((simdi - s.son_degisiklik) / 86400),
                        },
                    }
                )

        # Önerileri veritabanına kaydet
        self._oneri_kaydet(adaylar)
        logger.info("%d iyilestirme adayi bulundu", len(adaylar))
        return adaylar

    # ── Otomatik iyileştirme ───────────────────────────────────────

    def otomatik_iyilestir(self) -> int:
        """İyileştirme adaylarına otomatik düzeltmeler uygula.

        Yapılanlar:
        - Eksik metadata varsa YAML frontmatter'ını ekler
        - Benzer skill'ler için birleştirme notu ekler
        - Düşük başarılı skill'lere hata senaryosu bölümü ekler

        Returns:
            İyileştirilen skill sayısı.
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

        # İyileştirmeleri uygulandı olarak işaretle
        with self._vt._db() as db:
            db.execute(
                "UPDATE iyilestirme_onerileri SET uygulandi = 1 WHERE uygulandi = 0"
            )

        logger.info("%d skill iyilestirildi", iyilestirilen)
        return iyilestirilen

    # ── Rapor ──────────────────────────────────────────────────────

    def rapor_uret(self) -> str:
        """Kapsamlı iyileştirme raporu üret.

        Returns:
            İnsan tarafından okunabilir rapor metni.
        """
        # Tüm skill'leri tara
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

        # İyileştirme adayları
        adaylar = self.iyilestirme_adaylari_bul()
        uygulanan = 0
        with self._vt._db() as db:
            row = db.execute(
                "SELECT COUNT(*) as sayi FROM iyilestirme_onerileri WHERE uygulandi = 1"
            ).fetchone()
            uygulanan = row["sayi"] if row else 0

        # Genel başarı oranı
        genel_basari = 0.0
        if toplam_kullanim > 0:
            genel_basari = round(basarili_toplam / toplam_kullanim * 100, 1)

        # Rapor metni
        satirlar = [
            "╔══════════════════════════════════════════════════════════╗",
            "║     🔧 SKILL İYİLEŞTİRME RAPORU                        ║",
            "╚══════════════════════════════════════════════════════════╝",
            "",
            f"Tarih: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "── GENEL DURUM ──",
            f"  Taranan skill      : {len(tum_skilller)}",
            f"  Toplam kullanım    : {toplam_kullanim}",
            f"  Genel başarı oranı : %{genel_basari}",
            f"  İyileştirme adayı  : {len(adaylar)}",
            f"  Uygulanan iyileşt. : {uygulanan}",
            "",
            "── SKILL DETAYLARI ──",
        ]

        # Skill detaylarını sırala (en çok kullanılan -> en az)
        skill_detaylari.sort(key=lambda x: x["kullanim"], reverse=True)
        for sd in skill_detaylari[:20]:  # İlk 20
            basari_gostergesi = (
                "✅"
                if sd["basari_orani"] >= 70
                else ("⚠️" if sd["basari_orani"] >= 40 else "❌")
            )
            satirlar.append(
                f"  {basari_gostergesi} {sd['ad']} "
                f"(v{sd['versiyon']}, {sd['kategori'] or 'kategorisiz'})"
            )
            satirlar.append(
                f"     Kullanım: {sd['kullanim']} kez, "
                f"Başarı: %{sd['basari_orani']}, "
                f"Süre: {sd['ortalama_sure_ms']}ms"
            )

        if adaylar:
            satirlar.extend(
                [
                    "",
                    "── İYİLEŞTİRME ÖNERİLERİ ──",
                ]
            )
            # Önceliğe göre sırala
            adaylar.sort(key=lambda x: x["oncelik"], reverse=True)
            for i, aday in enumerate(adaylar[:10], 1):  # İlk 10
                tur_ikonlari = {
                    "dusuk_basari": "🔴",
                    "sik_kullanilan_dusuk_basari": "🟠",
                    "eksik_meta": "🟡",
                    "birlestir": "🔵",
                    "kullanilmayan": "⚪",
                }
                ikon = tur_ikonlari.get(aday["tur"], "⚫")
                satirlar.append(
                    f"  {i}. {ikon} [{aday['tur'].upper()}] {aday['skill_adi']}"
                )
                satirlar.append(f"     Öncelik: {aday['oncelik']}/10")
                satirlar.append(f"     {aday['aciklama']}")
        else:
            satirlar.extend(
                [
                    "",
                    "── İYİLEŞTİRME ÖNERİLERİ ──",
                    "  ✅ Tüm skill'ler iyi durumda. İyileştirme gerekmiyor.",
                ]
            )

        satirlar.extend(
            [
                "",
                "── SON İŞLEMLER ──",
                f"  Son otomatik iyileştirmede {uygulanan} skill güncellendi.",
                "",
            ]
        )

        # Raporu veritabanına kaydet
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

    # ── İç yardımcılar ─────────────────────────────────────────────

    def _skill_bilgisini_kaydet(self, bilgi: SkillBilgisi) -> None:
        """Skill bilgisini veritabanına kaydet/güncelle."""
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
        """Skill'de eksik metadata alanlarını bul."""
        eksik = []
        if not bilgi.aciklama:
            eksik.append("description/açıklama")
        if not bilgi.kategori:
            eksik.append("category/kategori")
        if not bilgi.tetikleyiciler:
            eksik.append("triggers/tetikleyiciler")
        return eksik

    def _benzerlik_skoru(self, s1: SkillBilgisi, s2: SkillBilgisi) -> float:
        """İki skill arasındaki benzerlik skoru (0.0-1.0)."""
        puan = 0.0
        toplam = 0.0

        # Kategori benzerliği
        toplam += 1.0
        if s1.kategori and s2.kategori and s1.kategori.lower() == s2.kategori.lower():
            puan += 1.0

        # Etiket benzerliği
        if s1.etiketler and s2.etiketler:
            s1_set = set(t.lower() for t in s1.etiketler)
            s2_set = set(t.lower() for t in s2.etiketler)
            toplam += 1.0
            if s1_set & s2_set:
                puan += len(s1_set & s2_set) / max(len(s1_set | s2_set), 1)

        # Tetikleyici benzerliği
        if s1.tetikleyiciler and s2.tetikleyiciler:
            s1_set = set(t.lower() for t in s1.tetikleyiciler)
            s2_set = set(t.lower() for t in s2.tetikleyiciler)
            toplam += 1.0
            if s1_set & s2_set:
                puan += len(s1_set & s2_set) / max(len(s1_set | s2_set), 1)

        # İsim benzerliği (anahtar kelime ortaklığı)
        if s1.ad and s2.ad:
            s1_kelime = set(s1.ad.lower().replace("-", " ").replace("_", " ").split())
            s2_kelime = set(s2.ad.lower().replace("-", " ").replace("_", " ").split())
            toplam += 1.0
            if s1_kelime & s2_kelime:
                puan += len(s1_kelime & s2_kelime) / max(len(s1_kelime | s2_kelime), 1)

        return puan / max(toplam, 1)

    def _oneri_kaydet(self, adaylar: list[dict]) -> None:
        """İyileştirme önerilerini veritabanına kaydet."""
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
            # Skill dosyasını bul
            skills_dir = self._skills_dizini
            for dosya in skills_dir.glob("*.md"):
                bilgi = self._ayristirici.dosyadan_oku(dosya)
                if bilgi and bilgi.ad == skill_adi:
                    icerik = dosya.read_text("utf-8", errors="replace")
                    meta = _SkillAyrıstırıcı.YAML_meta_ayristir(icerik)

                    # Eksik alanları tespit et
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

                    # Var olan YAML frontmatter'ına ekle veya yeni oluştur
                    if re.match(r"^---\s*\n.*?\n---", icerik, re.DOTALL):
                        # Mevcut frontmatter'ı güncelle
                        def _ekle_meta(m):
                            blok = m.group(0)
                            # Son ---'den önce ekle
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
                        # Yeni frontmatter oluştur
                        yeni_meta = "---\n" + "\n".join(eklenecek) + "\n---\n\n"
                        yeni_icerik = yeni_meta + icerik

                    dosya.write_text(yeni_icerik, encoding="utf-8")
                    logger.info(
                        "Meta iyilestirildi: %s (%s)", skill_adi, ", ".join(eklenecek)
                    )
                    return True
        except Exception as e:
            logger.warning("Meta iyilestirme hatasi: %s — %s", skill_adi, e)
        return False

    def _hata_senaryosu_ekle(self, skill_adi: str, veri: dict) -> bool:
        """Düşük başarılı skill'e hata senaryosu bölümü ekle."""
        try:
            skills_dir = self._skills_dizini
            for dosya in skills_dir.glob("*.md"):
                bilgi = self._ayristirici.dosyadan_oku(dosya)
                if bilgi and bilgi.ad == skill_adi:
                    icerik = dosya.read_text("utf-8", errors="replace")

                    # Zaten hata senaryosu var mı?
                    if "## Hata Senaryoları" in icerik or "## Pitfall" in icerik:
                        return False

                    # Başarı oranı bilgisi
                    basari = veri.get("basari_orani", 0)
                    kullanim = veri.get("kullanim", 0)

                    hata_bloku = (
                        "\n\n"
                        "## ⚠️ Hata Senaryoları\n"
                        "\n"
                        f"> Bu skill %{basari:.1f} başarı oranına sahip "
                        f"({kullanim} kullanım). Aşağıdaki hata senaryoları gözden geçirilmeli.\n"
                        "\n"
                        "### Bilinen Hatalar\n"
                        "- **Hata 1**: Açıklama eklenmeli\n"
                        "- **Hata 2**: Açıklama eklenmeli\n"
                        "\n"
                        "### Çözüm Önerileri\n"
                        "- Kullanım talimatları netleştirilmeli\n"
                        "- Beklenen çıktı formatı belirtilmeli\n"
                        "- Sınır durumlar (edge cases) belgelenmeli\n"
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
            logger.warning("Hata senaryosu ekleme hatasi: %s — %s", skill_adi, e)
        return False

    def _kullanilmayan_notu_ekle(self, skill_adi: str) -> bool:
        """Kullanılmayan skill'e gözden geçirme notu ekle."""
        try:
            skills_dir = self._skills_dizini
            for dosya in skills_dir.glob("*.md"):
                bilgi = self._ayristirici.dosyadan_oku(dosya)
                if bilgi and bilgi.ad == skill_adi:
                    icerik = dosya.read_text("utf-8", errors="replace")

                    if "---\n# GÖZDEN GEÇİR" in icerik or "---\n# REVIEW" in icerik:
                        return False

                    not_bloku = (
                        "\n\n"
                        "---\n"
                        "# GÖZDEN GEÇİR\n"
                        "\n"
                        "> ⏰ Bu skill 30 günden uzun süredir güncellenmemiş "
                        "ve hiç kullanılmamış. Kaldırılabilir veya güncellenebilir.\n"
                    )

                    yeni_icerik = icerik.rstrip() + not_bloku
                    dosya.write_text(yeni_icerik, encoding="utf-8")
                    logger.info("Kullanilmayan notu eklendi: %s", skill_adi)
                    return True
        except Exception as e:
            logger.warning("Kullanilmayan notu ekleme hatasi: %s — %s", skill_adi, e)
        return False

    # ── Ek yardımcılar ─────────────────────────────────────────────

    def en_cok_kullanilan_skilller(self, limit: int = 10) -> list[dict]:
        """En çok kullanılan skill'leri döndür."""
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
        """Son kullanımları döndür."""
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
        """Skill kullanım istatistiklerini sıfırla."""
        with self._vt._db() as db:
            if skill_adi:
                db.execute(
                    "DELETE FROM kullanim_gecmisi WHERE skill_adi = ?", (skill_adi,)
                )
            else:
                db.execute("DELETE FROM kullanim_gecmisi")
            logger.info(
                "Istatistikler sifirlandi%s",
                f" — {skill_adi}" if skill_adi else " (tum skill'ler)",
            )


# ── CLI kullanımı ──────────────────────────────────────────────────


def main() -> str:
    """CLI giriş noktası.

    Kullanım:
        python -m reymen.scripts.skill_iyilestirici
    """
    si = SkillIyilestirici()

    # 1. Skill'leri tara
    print("📂 Skill'ler taranıyor...")
    skill_sayisi = len(si.skill_dosyalarini_tara())
    print(f"   {skill_sayisi} skill bulundu")

    # 2. İyileştirme adaylarını bul
    print("\n🔍 İyileştirme adayları taranıyor...")
    adaylar = si.iyilestirme_adaylari_bul()
    print(f"   {len(adaylar)} aday bulundu")

    # 3. Otomatik iyileştir
    if adaylar:
        print("\n🛠️  Otomatik iyileştirme uygulanıyor...")
        iyilestirilen = si.otomatik_iyilestir()
        print(f"   {iyilestirilen} skill iyileştirildi")
    else:
        print("\n✅ İyileştirme gerekmiyor")
        iyilestirilen = 0

    # 4. Rapor üret
    print("\n📊 Rapor üretiliyor...")
    rapor = si.rapor_uret()
    print(rapor)

    return rapor


if __name__ == "__main__":
    main()
