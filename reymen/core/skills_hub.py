# -*- coding: utf-8 -*-
"""
skills_hub.py — Skills Hub: Topluluk skill'lerini kesfetme, indirme ve yonetme.

agentskills.io / skills.sh API'si uzerinden topluluk skill'lerini:
- Kesfeder (kategori bazli arama, metin arama)
- Metadata'sini gosterir (isim, aciklama, kategori, versiyon, yazar)
- Indirir ve reymen/cereyan/skills/ altina kurar
- Cron ile haftalik guncelleme yapar

Kullanim:
    from reymen.core.skills_hub import SkillsHub
    hub = SkillsHub()
    sonuclar = hub.ara("python test")
    hub.indir("python-testing-framework", kategori="Yazilim")
    hub.haftalik_guncelleme()
"""

from __future__ import annotations

import json
import logging
import sqlite3
import threading
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

# ── Sabitler ─────────────────────────────────────────────────────────────────

# skills.sh API'si (Mastra AI tarafindan isletilir, 34.000+ skill)
SKILLS_SH_API = "https://skills.sh/api/skills"

# agentskills.io spesifikasyon sayfasi
AGENTSKILLS_IO = "https://agentskills.io"

# Varsayilan kurulum dizini (reymen/cereyan/skills/)
PROJE_KOKU = Path(__file__).resolve().parent.parent  # reymen/
VARSAYILAN_SKILLS_DIZINI = PROJE_KOKU / "cereyan" / "skills"

# Veritabani: indirilen skill metadata'si
HUB_DB = PROJE_KOKU / "merkez_db" / "skills_hub.db"

# HTTP istek zaman asimi (saniye)
HTTP_TIMEOUT = 30

# Sayfalama varsayilanlari
VARSAYILAN_LIMIT = 20
MAKS_LIMIT = 100

_yazma_kilit = threading.Lock()


# ═══════════════════════════════════════════════════════════════════════════════
#  Veri Modelleri
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SkillMetadata:
    """Topluluk skill'inin metadata'si.

    Nitelikler:
        name: Skill'in kisa adi (ornek: "python-testing-framework")
        description: Aciklama metni
        category: Kategori (ornek: "Yazilim", "DevOps", "MLOps")
        version: Versyon numarasi (ornek: "1.0.0")
        author: Yazar adi veya GitHub kullanici adi
        repo_url: Kaynak repo URL'si
        skill_url: SKILL.md dogrudan URL'si
        tags: Etiket listesi
        weekly_installs: Haftalik indirme sayisi (varsa)
        kaynak: API kaynagi ("skills-sh")
        ham_veri: API'den gelen ham JSON (debug icin)
    """
    name: str = ""
    description: str = ""
    category: str = ""
    version: str = ""
    author: str = ""
    repo_url: str = ""
    skill_url: str = ""
    tags: list[str] = field(default_factory=list)
    weekly_installs: int = 0
    kaynak: str = "skills-sh"
    ham_veri: dict[str, Any] = field(default_factory=dict)


@dataclass
class IndirmeSonucu:
    """Skill indirme sonucu."""
    basarili: bool = False
    name: str = ""
    hedef_yol: str = ""
    hata: str = ""
    kategori: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
#  HTTP Yardimcilari
# ═══════════════════════════════════════════════════════════════════════════════

def _http_get(url: str, params: dict[str, Any] | None = None,
              timeout: int = HTTP_TIMEOUT) -> dict[str, Any] | list[Any] | None:
    """Genel HTTP GET istegi.

    Args:
        url: Hedef URL
        params: Query parametreleri (sozluk)
        timeout: Zaman asimi (saniye)

    Returns:
        JSON yaniti (dict veya list) veya None (hata durumunda)
    """
    if params:
        qs = urllib.parse.urlencode(
            {k: v for k, v in params.items() if v is not None}
        )
        tam_url = f"{url}?{qs}"
    else:
        tam_url = url

    logger.debug("HTTP GET: %s", tam_url[:200])

    try:
        req = urllib.request.Request(
            tam_url,
            headers={
                "User-Agent": "ReYMeN-SkillsHub/1.0",
                "Accept": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ham = resp.read().decode("utf-8", errors="replace")
            return json.loads(ham)
    except HTTPError as e:
        logger.warning("HTTP hatasi [%s]: %s — %s", e.code, tam_url[:100], e.reason)
        return None
    except URLError as e:
        logger.warning("URL hatasi [%s]: %s", tam_url[:100], e.reason)
        return None
    except (json.JSONDecodeError, OSError, TimeoutError) as e:
        logger.warning("JSON/okuma hatasi [%s]: %s", tam_url[:80], e)
        return None


def _indir_dosya(url: str, hedef: Path, timeout: int = HTTP_TIMEOUT) -> bool:
    """Bir dosyayi URL'den indirip hedef yola kaydeder.

    Args:
        url: Indirilecek dosyanin URL'si
        hedef: Kaydedilecek yerel yol
        timeout: Zaman asimi (saniye)

    Returns:
        True (basarili) / False (hata)
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "ReYMeN-SkillsHub/1.0",
                "Accept": "text/markdown, text/plain, */*",
            },
        )
        hedef.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(req, timeout=timeout) as kaynak:
            with open(hedef, "wb") as f:
                f.write(kaynak.read())
        logger.info("Dosya indirildi: %s -> %s", url, hedef)
        return True
    except Exception as e:
        logger.warning("Dosya indirme hatasi [%s]: %s", url[:80], e)
        return False


# ═══════════════════════════════════════════════════════════════════════════════
#  Veritabani Yonetimi
# ═══════════════════════════════════════════════════════════════════════════════

def _db_kur():
    """Skills Hub veritabanini olustur (varsa atla)."""
    HUB_DB.parent.mkdir(parents=True, exist_ok=True)
    with _yazma_kilit:
        con = sqlite3.connect(str(HUB_DB), timeout=15)
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
        try:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS hub_skills (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    name            TEXT NOT NULL UNIQUE,
                    description     TEXT NOT NULL DEFAULT '',
                    category        TEXT NOT NULL DEFAULT '',
                    version         TEXT NOT NULL DEFAULT '',
                    author          TEXT NOT NULL DEFAULT '',
                    repo_url        TEXT NOT NULL DEFAULT '',
                    skill_url       TEXT NOT NULL DEFAULT '',
                    tags            TEXT NOT NULL DEFAULT '',
                    weekly_installs INTEGER NOT NULL DEFAULT 0,
                    kaynak          TEXT NOT NULL DEFAULT 'skills-sh',
                    indirildi       INTEGER NOT NULL DEFAULT 0,
                    indirilme_tarihi TEXT,
                    hedef_yol       TEXT NOT NULL DEFAULT '',
                    son_guncelleme  TEXT NOT NULL DEFAULT (datetime('now')),
                    ham_json        TEXT NOT NULL DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_hub_category ON hub_skills(category);
                CREATE INDEX IF NOT EXISTS idx_hub_name     ON hub_skills(name);
                CREATE INDEX IF NOT EXISTS idx_hub_indirildi ON hub_skills(indirildi);

                CREATE TABLE IF NOT EXISTS hub_sync_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    baslama     TEXT NOT NULL,
                    bitis       TEXT,
                    durum       TEXT NOT NULL DEFAULT 'calisiyor',
                    yeni_sayi   INTEGER NOT NULL DEFAULT 0,
                    hata_sayi   INTEGER NOT NULL DEFAULT 0,
                    mesaj       TEXT
                );
            """)
            con.commit()
        except Exception as e:
            con.rollback()
            logger.warning("DB kurulum hatasi: %s", e)
        finally:
            con.close()


def _db_baglan() -> sqlite3.Connection:
    """Veritabanina baglan (WAL + timeout)."""
    con = sqlite3.connect(str(HUB_DB), timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    return con


# ═══════════════════════════════════════════════════════════════════════════════
#  Skills.sh API Arayuzu
# ═══════════════════════════════════════════════════════════════════════════════

def _skills_sh_ara(sorgu: str = "", kategori: str = "",
                   limit: int = VARSAYILAN_LIMIT,
                   offset: int = 0) -> list[SkillMetadata]:
    """skills.sh API'sinde skill ara.

    API: GET /api/skills?query=...&category=...&limit=...&offset=...

    Args:
        sorgu: Arama metni (bos = tumu)
        kategori: Kategori filtresi (bos = tumu)
        limit: Maksimum sonuc sayisi
        offset: Atlanacak sonuc sayisi (sayfalama)

    Returns:
        SkillMetadata listesi
    """
    params: dict[str, Any] = {
        "query": sorgu or None,
        "category": kategori or None,
        "limit": min(limit, MAKS_LIMIT),
        "offset": max(0, offset),
    }

    yanit = _http_get(SKILLS_SH_API, params)
    if yanit is None:
        logger.warning("skills.sh API yanit vermedi.")
        return []

    # skills.sh API'si farkli formatlarda yanit donebilir:
    # 1) {"skills": [...]} veya {"data": [...]}
    # 2) Dogrudan liste
    ham_liste: list[Any] = []
    if isinstance(yanit, list):
        ham_liste = yanit
    elif isinstance(yanit, dict):
        ham_liste = yanit.get("skills") or yanit.get("data") or yanit.get("results") or []

    sonuclar: list[SkillMetadata] = []
    for ham in ham_liste:
        if not isinstance(ham, dict):
            continue
        meta = _skills_sh_nesne_coz(ham)
        if meta:
            sonuclar.append(meta)

    return sonuclar


def _skills_sh_nesne_coz(ham: dict[str, Any]) -> SkillMetadata | None:
    """skills.sh API'sinden gelen ham JSON'i SkillMetadata'ye donusturur.

    Args:
        ham: API'den gelen JSON nesnesi

    Returns:
        SkillMetadata veya None (gecersizse)
    """
    if not ham:
        return None

    name = (ham.get("name") or ham.get("id") or ham.get("slug") or "").strip()
    if not name:
        return None

    # Kategori: "category" alani veya tag'lerden cikar
    kategori = (ham.get("category") or "").strip()

    # Etiketler
    tags_raw = ham.get("tags") or ham.get("labels") or []
    if isinstance(tags_raw, str):
        tags = [t.strip() for t in tags_raw.replace(",", " ").split() if t.strip()]
    elif isinstance(tags_raw, list):
        tags = [str(t).strip() for t in tags_raw if str(t).strip()]
    else:
        tags = []

    # Yazar
    author = (ham.get("author") or ham.get("owner") or ham.get("creator") or "").strip()

    # Repo URL
    repo_url = (ham.get("repo_url") or ham.get("repository") or ham.get("source") or "").strip()

    # Skill URL (SKILL.md'nin ham URL'si)
    skill_url = (ham.get("skill_url") or ham.get("url") or ham.get("download_url") or "").strip()
    # Eger dogrudan SKILL.md URL'si yoksa, repo URL'sinden turet
    if not skill_url and repo_url:
        if repo_url.endswith(".git"):
            repo_url = repo_url[:-4]
        if "github.com" in repo_url:
            # GitHub raw URL'si olustur
            skill_url = repo_url.replace("github.com", "raw.githubusercontent.com")
            skill_url = f"{skill_url}/main/SKILL.md"

    # Aciklama
    description = (ham.get("description") or ham.get("summary") or "").strip()
    # description cok uzunsa kisalt
    if len(description) > 500:
        description = description[:497] + "..."

    # Versiyon
    version = (ham.get("version") or "").strip()

    # Haftalik indirme
    try:
        weekly = int(ham.get("weekly_installs") or ham.get("installs") or 0)
    except (ValueError, TypeError):
        weekly = 0

    return SkillMetadata(
        name=name,
        description=description,
        category=kategori,
        version=version,
        author=author,
        repo_url=repo_url,
        skill_url=skill_url,
        tags=tags,
        weekly_installs=weekly,
        kaynak="skills-sh",
        ham_veri=ham,
    )


def _skills_sh_kategoriler() -> list[str]:
    """skills.sh API'sinden mevcut kategorileri alir.

    Returns:
        Kategori isimleri listesi (sirali)
    """
    # Tum skill'leri kucuk bir limit ile getirip kategorileri cikar
    # Not: skills.sh API'sinde dogrudan /api/categories endpoint'i yok,
    # bu yuzden arama yapip kategorileri topluyoruz.
    sonuclar = _skills_sh_ara(sorgu="", limit=100, offset=0)

    kategoriler: set[str] = set()
    for s in sonuclar:
        if s.category:
            kategoriler.add(s.category)

    return sorted(kategoriler)


# ═══════════════════════════════════════════════════════════════════════════════
#  Skills Hub Sinifi
# ═══════════════════════════════════════════════════════════════════════════════

class SkillsHub:
    """Skills Hub — topluluk skill'lerini kesfetme, indirme ve yonetme.

    agentskills.io / skills.sh API'si uzerinden:
    - Arama (kategori bazli, metin bazli)
    - Metadata gorme
    - Skill indirme ve kurma
    - Haftalik guncelleme (cron ile)

    Kullanim:
        hub = SkillsHub()
        sonuclar = hub.ara("python")
        hub.indir("python-testing", kategori="Yazilim")
        hub.haftalik_guncelleme()
    """

    def __init__(self, skills_dizini: str | Path | None = None):
        """
        Args:
            skills_dizini: Skill'lerin kurulacagi dizin
                          (None = reymen/cereyan/skills/)
        """
        self._skills_dizini = Path(skills_dizini) if skills_dizini else VARSAYILAN_SKILLS_DIZINI
        self._skills_dizini.mkdir(parents=True, exist_ok=True)
        _db_kur()

    # ── Arama ───────────────────────────────────────────────────────────

    def ara(self, sorgu: str = "", kategori: str = "",
            limit: int = VARSAYILAN_LIMIT, offset: int = 0,
            kaynak: str = "skills-sh") -> list[SkillMetadata]:
        """Topluluk skill'lerinde ara.

        Birden fazla kaynagi destekler:
          - "skills-sh": skills.sh API'si (34.000+ skill)
          - "yerel": Yerel veritabanindaki skill'ler

        Args:
            sorgu: Arama metni (bos = tumu listele)
            kategori: Kategori filtresi (ornek: "Yazilim", "DevOps")
            limit: Maksimum sonuc sayisi
            offset: Atlanacak sonuc sayisi
            kaynak: Kaynak ("skills-sh", "yerel")

        Returns:
            SkillMetadata listesi
        """
        if kaynak == "skills-sh":
            return _skills_sh_ara(
                sorgu=sorgu, kategori=kategori,
                limit=limit, offset=offset,
            )
        elif kaynak == "yerel":
            return self._yerel_ara(sorgu=sorgu, kategori=kategori, limit=limit)

        # Tum kaynaklar
        sonuclar: list[SkillMetadata] = []
        gorulen: set[str] = set()

        yerel = self._yerel_ara(sorgu=sorgu, kategori=kategori, limit=limit)
        for m in yerel:
            if m.name not in gorulen:
                gorulen.add(m.name)
                sonuclar.append(m)

        uzak = _skills_sh_ara(sorgu=sorgu, kategori=kategori, limit=limit, offset=offset)
        for m in uzak:
            if m.name not in gorulen and len(sonuclar) < limit:
                gorulen.add(m.name)
                sonuclar.append(m)

        return sonuclar[:limit]

    def _yerel_ara(self, sorgu: str = "", kategori: str = "",
                   limit: int = VARSAYILAN_LIMIT) -> list[SkillMetadata]:
        """Yerel veritabaninda ara (indirilmis skill'ler)."""
        con = _db_baglan()
        try:
            kosullar: list[str] = []
            params: list[Any] = []

            if sorgu:
                kosullar.append(
                    "(name LIKE ? OR description LIKE ? OR tags LIKE ?)"
                )
                like = f"%{sorgu}%"
                params.extend([like, like, like])

            if kategori:
                kosullar.append("category = ?")
                params.append(kategori)

            where = " AND ".join(kosullar) if kosullar else "1=1"
            rows = con.execute(
                f"""SELECT name, description, category, version, author,
                           repo_url, skill_url, tags, weekly_installs, kaynak
                    FROM hub_skills
                    WHERE {where}
                    ORDER BY weekly_installs DESC, name ASC
                    LIMIT ?""",
                params + [limit],
            ).fetchall()

            sonuclar = []
            for r in rows:
                tags = [t.strip() for t in (r["tags"] or "").split(",") if t.strip()]
                sonuclar.append(SkillMetadata(
                    name=r["name"],
                    description=r["description"],
                    category=r["category"],
                    version=r["version"],
                    author=r["author"],
                    repo_url=r["repo_url"],
                    skill_url=r["skill_url"],
                    tags=tags,
                    weekly_installs=r["weekly_installs"],
                    kaynak=r["kaynak"],
                ))
            return sonuclar
        finally:
            con.close()

    # ── Kategoriler ─────────────────────────────────────────────────────

    def kategoriler(self, kaynak: str = "skills-sh") -> list[str]:
        """Mevcut kategorileri listele.

        Args:
            kaynak: "skills-sh" (uzak) veya "yerel" (indirilmis skill'lerden)

        Returns:
            Kategori isimleri (sirali)
        """
        if kaynak == "skills-sh":
            return _skills_sh_kategoriler()

        con = _db_baglan()
        try:
            rows = con.execute(
                "SELECT DISTINCT category FROM hub_skills WHERE category != '' ORDER BY category"
            ).fetchall()
            return [r["category"] for r in rows]
        finally:
            con.close()

    # ── Metadata Detayi ─────────────────────────────────────────────────

    def metadata(self, name: str) -> SkillMetadata | None:
        """Bir skill'in detayli metadata'sini getir.

        Once yerel DB'ye bakar, bulamazsa skills.sh API'sinden sorgular.

        Args:
            name: Skill adi

        Returns:
            SkillMetadata veya None
        """
        # Yerel DB'de ara
        con = _db_baglan()
        try:
            row = con.execute(
                """SELECT name, description, category, version, author,
                          repo_url, skill_url, tags, weekly_installs, kaynak, ham_json
                   FROM hub_skills WHERE name = ?""",
                (name,),
            ).fetchone()
            if row:
                tags = [t.strip() for t in (row["tags"] or "").split(",") if t.strip()]
                return SkillMetadata(
                    name=row["name"],
                    description=row["description"],
                    category=row["category"],
                    version=row["version"],
                    author=row["author"],
                    repo_url=row["repo_url"],
                    skill_url=row["skill_url"],
                    tags=tags,
                    weekly_installs=row["weekly_installs"],
                    kaynak=row["kaynak"],
                )
        finally:
            con.close()

        # Uzakta ara
        sonuclar = _skills_sh_ara(sorgu=name, limit=5)
        for s in sonuclar:
            if s.name == name:
                return s
        return None

    # ── Skill Indirme ───────────────────────────────────────────────────

    def indir(self, name: str, kategori: str = "",
              force: bool = False) -> IndirmeSonucu:
        """Bir skill'i skills.sh'den indir ve kur.

        Indirme akisi:
        1. Skill metadata'sini al
        2. SKILL.md icerigini indir
        3. Hedef dizine kaydet (reymen/cereyan/skills/<kategori>/<name>.md)
        4. Veritabanina kaydet

        Args:
            name: Skill adi (veya identifier)
            kategori: Hedef kategori (ornek: "Yazilim", "DevOps")
            force: True ise uzerine yaz

        Returns:
            IndirmeSonucu
        """
        # Metadata al
        meta = self.metadata(name)
        if meta is None:
            # skills.sh'de tekrar ara
            sonuclar = _skills_sh_ara(sorgu=name, limit=5)
            for s in sonuclar:
                if s.name == name:
                    meta = s
                    break

        if meta is None:
            return IndirmeSonucu(
                basarili=False, name=name, hata=f"Skill bulunamadi: {name}"
            )

        # Kategori belirle
        hedef_kategori = kategori or meta.category or "Genel"

        # Hedef dosya yolu
        hedef_dizin = self._skills_dizini / hedef_kategori
        hedef_dosya = hedef_dizin / f"{meta.name}.md"

        # Zaten var mi kontrol et
        if hedef_dosya.exists() and not force:
            return IndirmeSonucu(
                basarili=True, name=name,
                hedef_yol=str(hedef_dosya),
                kategori=hedef_kategori,
            )

        # SKILL.md URL'si belirle
        skill_url = meta.skill_url
        if not skill_url:
            # skills.sh API'sinden dogrudan icerik almayi dene
            # API: GET /api/skills/:owner/:repo/:skillId/files
            # Daha basit: repo URL'sinden SKILL.md'yi bul
            if meta.repo_url and "github.com" in meta.repo_url:
                # Raw GitHub URL'si olustur
                raw_url = meta.repo_url.replace("github.com", "raw.githubusercontent.com")
                raw_url = raw_url.rstrip("/")
                if raw_url.endswith(".git"):
                    raw_url = raw_url[:-4]
                skill_url = f"{raw_url}/main/SKILL.md"

        if not skill_url:
            return IndirmeSonucu(
                basarili=False, name=name,
                hata=f"Skill URL'si bulunamadi: {name}"
            )

        # Indir
        basari = _indir_dosya(skill_url, hedef_dosya)
        if not basari:
            return IndirmeSonucu(
                basarili=False, name=name, kategori=hedef_kategori,
                hata=f"Indirme basarisiz: {skill_url}"
            )

        # Veritabanina kaydet
        self._indirme_kaydet(meta, hedef_kategori, str(hedef_dosya))

        logger.info("Skill basariyla indirildi: %s -> %s", name, hedef_dosya)
        return IndirmeSonucu(
            basarili=True, name=name,
            hedef_yol=str(hedef_dosya),
            kategori=hedef_kategori,
        )

    def _indirme_kaydet(self, meta: SkillMetadata, kategori: str,
                        hedef_yol: str):
        """Indirilen skill'i veritabanina kaydet."""
        tags_str = ", ".join(meta.tags)
        simdi = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        ham_json = json.dumps(meta.ham_veri, ensure_ascii=False)

        with _yazma_kilit:
            con = _db_baglan()
            try:
                con.execute(
                    """INSERT OR REPLACE INTO hub_skills
                       (name, description, category, version, author,
                        repo_url, skill_url, tags, weekly_installs, kaynak,
                        indirildi, indirilme_tarihi, hedef_yol, son_guncelleme, ham_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?, ?, ?)""",
                    (
                        meta.name, meta.description[:500], kategori,
                        meta.version, meta.author,
                        meta.repo_url, meta.skill_url,
                        tags_str, meta.weekly_installs, meta.kaynak,
                        simdi, hedef_yol, simdi, ham_json,
                    ),
                )
                con.commit()
            except Exception as e:
                con.rollback()
                logger.warning("Indirme kayit hatasi [%s]: %s", meta.name, e)
            finally:
                con.close()

    # ── Toplu Indirme / Guncelleme ──────────────────────────────────────

    def haftalik_guncelleme(self, kategori: str = "",
                            max_indir: int = 10) -> dict[str, Any]:
        """Haftalik skills hub guncellemesi (cron icin).

        Akis:
        1. skills.sh'den populer skill'leri getir
        2. Henuz indirilmemis olanlari indir
        3. Indirilmis olanlari guncelle
        4. Sync log'una kaydet

        Args:
            kategori: Sadece belirli bir kategoriyi guncelle (bos = tumu)
            max_indir: Maksimum indirilecek skill sayisi

        Returns:
            {
                "yeni": int,        # Yeni indirilenler
                "guncellenen": int, # Guncellenenler
                "hata": int,        # Hata sayisi
                "toplam": int,      # Toplam taranan
            }
        """
        baslama = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        logger.info("Skills Hub haftalik guncelleme basladi (kategori=%s, max=%d)",
                     kategori or "(tumu)", max_indir)

        # skills.sh'den skill'leri getir
        uzak_skills = _skills_sh_ara(sorgu="", kategori=kategori,
                                      limit=max_indir * 3, offset=0)
        if not uzak_skills:
            logger.warning("skills.sh'den skill alinamadi, guncelleme atlandi.")
            self._sync_log_kaydet(baslama, durum="hata",
                                   mesaj="API yanit vermedi")
            return {"yeni": 0, "guncellenen": 0, "hata": 1, "toplam": 0}

        yeni = 0
        guncellenen = 0
        hata_say = 0

        # Zaten indirilmis olanlari tespit et
        con = _db_baglan()
        try:
            indirilmis = set(
                r["name"] for r in con.execute(
                    "SELECT name FROM hub_skills WHERE indirildi = 1"
                ).fetchall()
            )
        finally:
            con.close()

        for skill in uzak_skills[:max_indir]:
            try:
                if skill.name in indirilmis:
                    # Zaten indirilmis — sadece metadata'yi guncelle
                    self._metadata_guncelle(skill)
                    guncellenen += 1
                else:
                    # Yeni skill — indir
                    sonuc = self.indir(skill.name, force=False)
                    if sonuc.basarili:
                        yeni += 1
                    else:
                        hata_say += 1
                        logger.warning("Indirme basarisiz [%s]: %s",
                                        skill.name, sonuc.hata)
            except Exception as e:
                hata_say += 1
                logger.warning("Guncelleme hatasi [%s]: %s", skill.name, e)

        # Sync log'una kaydet
        durum = "tamam" if hata_say == 0 else "kismi"
        self._sync_log_kaydet(
            baslama, durum=durum,
            yeni=yeni, hata=hata_say,
            mesaj=f"{yeni} yeni, {guncellenen} guncel, {hata_say} hata",
        )

        logger.info("Skills Hub guncelleme tamam: %d yeni, %d guncel, %d hata",
                     yeni, guncellenen, hata_say)
        return {
            "yeni": yeni,
            "guncellenen": guncellenen,
            "hata": hata_say,
            "toplam": len(uzak_skills[:max_indir]),
        }

    def _metadata_guncelle(self, meta: SkillMetadata):
        """Veritabanindaki skill metadata'sini guncelle."""
        tags_str = ", ".join(meta.tags)
        simdi = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        with _yazma_kilit:
            con = _db_baglan()
            try:
                con.execute(
                    """UPDATE hub_skills SET
                        description = ?, category = ?, version = ?,
                        author = ?, repo_url = ?, skill_url = ?,
                        tags = ?, weekly_installs = ?, kaynak = ?,
                        son_guncelleme = ?
                       WHERE name = ?""",
                    (
                        meta.description[:500],
                        meta.category or "",
                        meta.version,
                        meta.author,
                        meta.repo_url,
                        meta.skill_url,
                        tags_str,
                        meta.weekly_installs,
                        meta.kaynak,
                        simdi,
                        meta.name,
                    ),
                )
                con.commit()
            except Exception as e:
                con.rollback()
                logger.warning("Metadata guncelleme hatasi [%s]: %s", meta.name, e)
            finally:
                con.close()

    def _sync_log_kaydet(self, baslama: str, durum: str = "tamam",
                         yeni: int = 0, hata: int = 0,
                         mesaj: str = ""):
        """Sync log'una kayit ekle."""
        bitis = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        with _yazma_kilit:
            con = _db_baglan()
            try:
                con.execute(
                    """INSERT INTO hub_sync_log
                       (baslama, bitis, durum, yeni_sayi, hata_sayi, mesaj)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (baslama, bitis, durum, yeni, hata, mesaj[:500]),
                )
                con.commit()
            except Exception as e:
                con.rollback()
                logger.warning("Sync log kayit hatasi: %s", e)
            finally:
                con.close()

    # ── Durum / Istatistik ──────────────────────────────────────────────

    def durum(self) -> dict[str, Any]:
        """Skills Hub durumunu goster.

        Returns:
            {
                "toplam_skill": int,      # Veritabanindaki toplam skill
                "indirilen": int,          # Indirilen skill sayisi
                "kategoriler": [str],      # Mevcut kategoriler
                "son_sync": str,           # Son senkronizasyon tarihi
                "skills_dizini": str,      # Skills dizini yolu
            }
        """
        con = _db_baglan()
        try:
            toplam = con.execute("SELECT COUNT(*) FROM hub_skills").fetchone()[0]
            indirilen = con.execute(
                "SELECT COUNT(*) FROM hub_skills WHERE indirildi = 1"
            ).fetchone()[0]

            son_sync_row = con.execute(
                "SELECT bitis FROM hub_sync_log WHERE durum IN ('tamam', 'kismi') ORDER BY id DESC LIMIT 1"
            ).fetchone()
            son_sync = son_sync_row["bitis"] if son_sync_row else ""

            kategoriler_row = con.execute(
                "SELECT DISTINCT category FROM hub_skills WHERE category != '' ORDER BY category"
            ).fetchall()
            kategoriler = sorted(set(r["category"] for r in kategoriler_row))
        finally:
            con.close()

        return {
            "toplam_skill": toplam,
            "indirilen": indirilen,
            "kategoriler": kategoriler,
            "son_sync": son_sync,
            "skills_dizini": str(self._skills_dizini),
        }

    def indirilenler(self, kategori: str = "",
                     limit: int = 50) -> list[dict[str, Any]]:
        """Indirilen skill'lerin listesi.

        Args:
            kategori: Kategori filtresi (bos = tumu)
            limit: Maksimum sonuc

        Returns:
            [{"name", "description", "category", "version", "author",
              "hedef_yol", "indirilme_tarihi"}, ...]
        """
        con = _db_baglan()
        try:
            if kategori:
                rows = con.execute(
                    """SELECT name, description, category, version, author,
                              hedef_yol, indirilme_tarihi
                       FROM hub_skills
                       WHERE indirildi = 1 AND category = ?
                       ORDER BY indirilme_tarihi DESC
                       LIMIT ?""",
                    (kategori, limit),
                ).fetchall()
            else:
                rows = con.execute(
                    """SELECT name, description, category, version, author,
                              hedef_yol, indirilme_tarihi
                       FROM hub_skills
                       WHERE indirildi = 1
                       ORDER BY indirilme_tarihi DESC
                       LIMIT ?""",
                    (limit,),
                ).fetchall()

            return [
                {
                    "name": r["name"],
                    "description": r["description"],
                    "category": r["category"],
                    "version": r["version"],
                    "author": r["author"],
                    "hedef_yol": r["hedef_yol"],
                    "indirilme_tarihi": r["indirilme_tarihi"],
                }
                for r in rows
            ]
        finally:
            con.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  Cron / CLI Yardimcilari
# ═══════════════════════════════════════════════════════════════════════════════

def cron_haftalik_guncelleme(kategori: str = "",
                             max_indir: int = 10) -> dict[str, Any]:
    """Haftalik Skills Hub guncellemesi — cron job'u icin dogrudan cagri.

    Ornek cron tanimi (haftada bir, Pazartesi 03:00):
        0 3 * * 1 python -c "from reymen.core.skills_hub import cron_haftalik_guncelleme; cron_haftalik_guncelleme()"

    Args:
        kategori: Kategori filtrelemesi (bos = tumu)
        max_indir: Maksimum indirilecek skill

    Returns:
        Guncelleme sonucu (sozluk)
    """
    hub = SkillsHub()
    return hub.haftalik_guncelleme(kategori=kategori, max_indir=max_indir)


def hub_durumu() -> dict[str, Any]:
    """Skills Hub durumunu goster (CLI/dis baglanti icin).

    Returns:
        Durum bilgisi (sozluk)
    """
    hub = SkillsHub()
    return hub.durum()


# ═══════════════════════════════════════════════════════════════════════════════
#  Dogrudan Calistirma
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    hub = SkillsHub()

    if len(sys.argv) > 1:
        komut = sys.argv[1].lower()

        if komut == "ara":
            sorgu = sys.argv[2] if len(sys.argv) > 2 else ""
            kategori = sys.argv[3] if len(sys.argv) > 3 else ""
            sonuclar = hub.ara(sorgu=sorgu, kategori=kategori, limit=10)
            print(f"\n=== Arama Sonuclari: {sorgu or '(tumu)'} ===")
            for s in sonuclar:
                kat = f"[{s.category}]" if s.category else ""
                print(f"  {s.name} {kat} — {s.description[:60]}")
            print(f"  Toplam: {len(sonuclar)} sonuc\n")

        elif komut == "indir":
            if len(sys.argv) < 3:
                print("Kullanim: python skills_hub.py indir <skill_adi> [kategori]")
                sys.exit(1)
            name = sys.argv[2]
            kategori = sys.argv[3] if len(sys.argv) > 3 else ""
            sonuc = hub.indir(name, kategori=kategori)
            if sonuc.basarili:
                print(f"\n✓ Indirildi: {sonuc.name} -> {sonuc.hedef_yol}\n")
            else:
                print(f"\n✗ Hata: {sonuc.hata}\n")

        elif komut == "kategoriler":
            kats = hub.kategoriler()
            print(f"\n=== Kategoriler ({len(kats)}) ===")
            for k in kats:
                print(f"  - {k}")
            print()

        elif komut == "guncelle":
            kategori = sys.argv[2] if len(sys.argv) > 2 else ""
            sonuc = hub.haftalik_guncelleme(kategori=kategori, max_indir=10)
            print(f"\n=== Guncelleme Sonucu ===")
            print(f"  Yeni: {sonuc['yeni']}")
            print(f"  Guncellenen: {sonuc['guncellenen']}")
            print(f"  Hata: {sonuc['hata']}")
            print(f"  Toplam: {sonuc['toplam']}\n")

        elif komut == "durum":
            d = hub.durum()
            print(f"\n=== Skills Hub Durumu ===")
            print(f"  Toplam skill: {d['toplam_skill']}")
            print(f"  Indirilen: {d['indirilen']}")
            print(f"  Kategoriler: {', '.join(d['kategoriler'])}")
            print(f"  Son sync: {d['son_sync'] or '(hic)'}")
            print(f"  Dizin: {d['skills_dizini']}\n")

        elif komut == "indirilenler":
            kategori = sys.argv[2] if len(sys.argv) > 2 else ""
            liste = hub.indirilenler(kategori=kategori)
            print(f"\n=== Indirilen Skill'ler ({len(liste)}) ===")
            for s in liste:
                print(f"  {s['name']} [{s['category']}] — {s['description'][:50]}")
            print()

        else:
            print(f"Bilinmeyen komut: {komut}")
            print("Kullanilabilir: ara, indir, kategoriler, guncelle, durum, indirilenler")

    else:
        # Varsayilan: durum goster
        d = hub.durum()
        print(f"\n=== Skills Hub ===")
        print(f"  Durum: {d['toplam_skill']} skill kayitli, {d['indirilen']} indirilmis")
        print(f"  Kullanim: python skills_hub.py <komut>")
        print(f"  Komutlar: ara, indir, kategoriler, guncelle, durum, indirilenler\n")
