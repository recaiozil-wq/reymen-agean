# -*- coding: utf-8 -*-
"""
skill_shrink.py â€” Skill shrinking tool.

Detects 10KB+ or 300+ line skills, shrinks bloated content,
splits sections that can be moved to references/ subfolder.

Usage (via CLI):
    reymen skill shrink --dry-run     # detect only
    reymen skill shrink --apply       # apply
    reymen skill shrink --stats       # statistics
"""

from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# â”€â”€ Renkler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_R = "\033[0m"
_C = "\033[96m"
_G = "\033[92m"
_Y = "\033[93m"
_B = "\033[94m"
_D = "\033[2m"
_RED = "\033[91m"


def _c(t):
    return f"{_C}{t}{_R}"


def _g(t):
    return f"{_G}{t}{_R}"


def _y(t):
    return f"{_Y}{t}{_R}"


def _b(t):
    return f"{_B}{t}{_R}"


def _d(t):
    return f"{_D}{t}{_R}"


def _r(t):
    return f"{_RED}{t}{_R}"


# â”€â”€ VarsayÄ±lan eÅŸikler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_BOYUT_ESIK = 10 * 1024  # 10 KB
_SATIR_ESIK = 300  # 300 satÄ±r

# â”€â”€ ÅiÅŸkinlik belirteçleri (regex desenleri) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_SISKINLIK_DESENLERI = [
    # Uzun kod örnekleri
    (r"```\w*\n.{300,}?```", "uzun_kod_ornegi"),
    # Gereksiz açÄ±klama bloklarÄ± (sadece ilk 10000 karakterde ara)
    (
        r"(AÅŸaÄŸÄ±daki|AÅŸaÄŸÄ±da|Åu ÅŸekilde|Bu bölümde|Ã–ncelikle|DetaylÄ± olarak)\s[^.]{200,}\.",
        "gereksiz_aciklama",
    ),
    # Uzun YAML frontmatter
    (r"^---\n(?:.+\n){20,}---", "asiri_frontmatter"),
    # AÅŸÄ±rÄ± örnek listeleri
    (r"\n(?:- .+\n){20,}", "asiri_ornek_liste"),
    # Tekrarlayan emoji notlarÄ±
    (r"^(?:âš ï¸|âœ…|âŒ|ğŸ“Œ|ğŸ’¡|ğŸ”‘|â„¹ï¸).*", "tekrar_uyari"),
    # Ã‡ok fazla baÅŸlÄ±k alt alta
    (r"^##.*\n(?:##.*\n){10,}", "asiri_alt_baslik"),
]

# â”€â”€ references/ taÅŸÄ±nabilecek bölüm desenleri (satÄ±r bazlÄ±, basit) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_REFERENCE_BOLUMLER = [
    r"## (?:Referanslar|References|Kaynaklar|Resources|Appendix|Ek)\s*\n",
    r"## (?:Ã–rnek(?:ler)?|Examples|Code\s*Examples)\s*\n",
    r"## (?:Tam\s*Ã‡Ä±ktÄ±|Output|Log|Debug)\s*\n",
]


def _bytes_insan(b: int) -> str:
    """Bayt deÄŸerini insan okunabilir formata çevir."""
    if b < 1024:
        return f"{b} B"
    elif b < 1024 * 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b / (1024 * 1024):.1f} MB"


def _sayfada_kac_satir(md_yol: Path) -> int:
    """Bir .md dosyasÄ±ndaki satÄ±r sayÄ±sÄ±nÄ± döndürür."""
    try:
        with open(md_yol, "r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def _frontmatter_parse(icerik: str) -> Dict[str, Any]:
    """YAML frontmatter'Ä± basitçe parse eder."""
    meta: Dict[str, Any] = {}
    if not icerik.startswith("---"):
        return meta
    end = icerik.find("---", 3)
    if end == -1:
        return meta
    frontmatter = icerik[3:end].strip()
    for satir in frontmatter.splitlines():
        if ":" not in satir:
            continue
        key, _, val = satir.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if not val:
            continue
        # Liste deÄŸer
        if val.startswith("[") and val.endswith("]"):
            val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",")]
        meta[key] = val
    return meta


def _determine_category(filepath: Path, skills_root: Path, meta: Dict[str, Any]) -> str:
    """Skill kategorisini belirler."""
    # Ã–nce frontmatter'dan
    cat = meta.get("category", "")
    if cat and cat != "genel" and cat != "general":
        return str(cat)

    # Sonra dosya yolu hiyerarÅŸisinden
    rel = filepath.relative_to(skills_root)
    parts = rel.parts
    if len(parts) > 1:
        return parts[0]
    return "genel"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tarama
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _tara_skill_dizini(skills_yolu: Path) -> List[Dict[str, Any]]:
    """Bir skill dizinini tarar ve skill bilgilerini döndürür."""
    sonuc: List[Dict[str, Any]] = []
    if not skills_yolu.exists():
        return sonuc

    for md_yol in sorted(skills_yolu.rglob("*.md")):
        # .md altÄ±ndaki .md'leri atla
        if ".ReYMeN" in md_yol.parts:
            continue
        if "node_modules" in md_yol.parts:
            continue
        if ".git" in md_yol.parts:
            continue

        try:
            icerik = md_yol.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        boyut = len(icerik.encode("utf-8"))
        satir = len(icerik.splitlines())
        meta = _frontmatter_parse(icerik)

        sonuc.append(
            {
                "yol": md_yol,
                "boyut": boyut,
                "satir": satir,
                "meta": meta,
                "ad": meta.get("name", md_yol.stem),
                "kategori": _determine_category(md_yol, skills_yolu, meta),
                "icerik": icerik,  # Cache for later use
            }
        )

    return sonuc


def _siskinlik_analizi(icerik: str) -> List[Dict[str, Any]]:
    """Bir skill içeriÄŸindeki ÅŸiÅŸkinlik bölgelerini tespit eder."""
    bulgular: List[Dict[str, Any]] = []
    for desen, etiket in _SISKINLIK_DESENLERI:
        try:
            for m in re.finditer(desen, icerik, re.MULTILINE | re.DOTALL):
                bulgular.append(
                    {
                        "etiket": etiket,
                        "baslangic": m.start(),
                        "bitis": m.end(),
                        "uzunluk": m.end() - m.start(),
                        "eslesen": m.group()[:100],
                    }
                )
        except re.error:
            continue

    # SÄ±rala: en büyükten en küçüÄŸe
    bulgular.sort(key=lambda b: b["uzunluk"], reverse=True)
    return bulgular


def _references_bolumleri_bul(icerik: str) -> List[Dict[str, Any]]:
    """references/ klasörüne taÅŸÄ±nabilecek bölümleri bulur."""
    bolumler: List[Dict[str, Any]] = []
    for desen in _REFERENCE_BOLUMLER:
        try:
            for m in re.finditer(desen, icerik, re.MULTILINE | re.DOTALL):
                bolumler.append(
                    {
                        "baslangic": m.start(),
                        "bitis": m.end(),
                        "uzunluk": m.end() - m.start(),
                        "icerik_ilk_100": m.group()[:100],
                    }
                )
        except re.error:
            continue
    bolumler.sort(key=lambda b: b["uzunluk"], reverse=True)
    return bolumler


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Küçültme Ä°ÅŸlemleri
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _trim_kod_ornekleri(icerik: str) -> Tuple[str, List[str]]:
    """Uzun kod örneklerini kÄ±saltÄ±r, çÄ±karÄ±lanlarÄ± döndürür."""
    cikarilan: List[str] = []
    yeni_icerik = icerik

    # Ã‡ok uzun kod bloklarÄ±nÄ± (300+ karakter) kÄ±salt
    kod_blok_deseni = r"(```\w*\n)([\s\S]{300,}?)(```)"

    def _kod_kisalt(m):
        bas = m.group(1)
        kod = m.group(2)
        bit = m.group(3)
        satirlar = kod.splitlines()
        if len(satirlar) <= 5:
            return m.group(0)
        # Ä°lk 3 + son 2 satÄ±rÄ± tut
        tutulan = (
            satirlar[:3]
            + ["... (orta kÄ±sÄ±m kÄ±saltÄ±ldÄ±, tamamÄ± references/ klasöründe)"]
            + satirlar[-2:]
        )
        cikarilan.append(kod)
        return bas + "\n".join(tutulan) + "\n" + bit

    yeni_icerik = re.sub(kod_blok_deseni, _kod_kisalt, yeni_icerik, flags=re.DOTALL)
    return yeni_icerik, cikarilan


def _trim_gereksiz_aciklamalar(icerik: str) -> str:
    """Gereksiz açÄ±klamalarÄ± kÄ±saltÄ±r."""
    yeni_icerik = icerik
    desenler = [
        (
            r"(AÅŸaÄŸÄ±daki|AÅŸaÄŸÄ±da|Åu ÅŸekilde|Bu bölümde|Ã–ncelikle|DetaylÄ± olarak) [^.]{200,}\.",
            "",
        ),
        (r"\n\n(?:Not|UyarÄ±|Info|Warning|Note):[^\n]{200,}", ""),
    ]
    for desen, _ in desenler:
        yeni_icerik = re.sub(desen, "", yeni_icerik, count=5)
    return yeni_icerik


def _trim_asiri_frontmatter(icerik: str) -> Tuple[str, Dict[str, Any]]:
    """AÅŸÄ±rÄ± büyük frontmatter'Ä± kÄ±saltÄ±r, kritik alanlarÄ± tutar."""
    if not icerik.startswith("---"):
        return icerik, {}
    end = icerik.find("---", 3)
    if end == -1:
        return icerik, {}

    frontmatter_str = icerik[3:end]
    satirlar = frontmatter_str.strip().splitlines()
    if len(satirlar) <= 15:
        return icerik, {}

    # Kritik alanlarÄ± tut
    kritik_alanlar = {
        "name",
        "title",
        "description",
        "category",
        "tags",
        "version",
        "audience",
        "triggers",
    }
    tutulacak: List[str] = []
    cikarilan: Dict[str, str] = {}
    for satir in satirlar:
        if ":" in satir:
            key = satir.split(":", 1)[0].strip().lower()
            if key in kritik_alanlar:
                tutulacak.append(satir)
            else:
                cikarilan[satir.split(":", 1)[0].strip()] = satir

    yeni_fm = "\n".join(tutulacak)
    yeni_icerik = "---\n" + yeni_fm + "\n---" + icerik[end + 3 :]
    return yeni_icerik, cikarilan


def _trim_asiri_listeler(icerik: str) -> str:
    """20+ elemanlÄ± listeleri kÄ±saltÄ±r."""
    yeni_icerik = icerik
    # ArdÄ±ÅŸÄ±k 20+ liste elemanÄ±nÄ± bul
    liste_deseni = r"(\n(?:- .+\n){20,})"

    def _liste_kisalt(m):
        liste = m.group(1)
        satirlar = [s for s in liste.splitlines() if s.strip().startswith("- ")]
        if len(satirlar) <= 20:
            return liste
        # Ä°lk 10 + son 5 tut
        tut = "\n".join(
            satirlar[:10]
            + ["... (liste kÄ±saltÄ±ldÄ±, tamamÄ± references/ klasöründe)"]
            + satirlar[-5:]
        )
        return "\n" + tut

    yeni_icerik = re.sub(liste_deseni, _liste_kisalt, yeni_icerik, flags=re.DOTALL)
    return yeni_icerik


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ana Ä°ÅŸlem
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class SkillShrink:
    """Skill küçültme aracÄ±.

    Parametreler:
        skills_dizinleri: Skill dizinleri listesi (Path).
    """

    def __init__(self, skills_dizinleri: List[Path]) -> None:
        self._dizinler = skills_dizinleri
        self._tum_skills: List[Dict[str, Any]] = []

    def tara(self) -> List[Dict[str, Any]]:
        """Tüm skill dizinlerini tarar, ÅŸiÅŸkin olanlarÄ± döndürür."""
        tum: List[Dict[str, Any]] = []
        for dizin in self._dizinler:
            tum.extend(_tara_skill_dizini(dizin))

        self._tum_skills = tum
        return tum

    def sisbul(
        self, skills: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """ÅiÅŸkin skill'leri tespit eder.

        DönüÅŸ: Her biri için ÅŸiÅŸkinlik bilgisi içeren sözlük listesi.
        """
        hedef = skills or self._tum_skills
        sis_skills: List[Dict[str, Any]] = []

        for s in hedef:
            sis = False
            neden: List[str] = []

            # Boyut/satÄ±r eÅŸiÄŸi
            if s["boyut"] >= _BOYUT_ESIK:
                sis = True
                neden.append(
                    f"boyut ({_bytes_insan(s['boyut'])} >= {_bytes_insan(_BOYUT_ESIK)})"
                )
            if s["satir"] >= _SATIR_ESIK:
                sis = True
                neden.append(f"{s['satir']} satir >= {_SATIR_ESIK} satir")

            if not sis:
                continue

            # DetaylÄ± ÅŸiÅŸkinlik analizi (sadece eÅŸiÄŸi geçenler)
            icerik = s.get("icerik", "")
            if not icerik:
                try:
                    icerik = s["yol"].read_text(encoding="utf-8", errors="replace")
                except Exception:
                    icerik = ""

            sis_bul = _siskinlik_analizi(icerik)
            ref_bul = _references_bolumleri_bul(icerik)

            toplam_sis_boyut = sum(b["uzunluk"] for b in sis_bul)
            toplam_ref_boyut = sum(b["uzunluk"] for b in ref_bul)

            sis_skills.append(
                {
                    **s,
                    "neden": neden,
                    "siskinlik_bulgulari": sis_bul,
                    "references_bolumleri": ref_bul,
                    "toplam_sis_boyut": toplam_sis_boyut,
                    "toplam_ref_boyut": toplam_ref_boyut,
                    "icerik": icerik,
                }
            )

        # Ã–nce en ÅŸiÅŸkin olanlarÄ± göster
        sis_skills.sort(key=lambda x: x["toplam_sis_boyut"], reverse=True)
        return sis_skills

    def shrink(self, sisli: Dict[str, Any], dry_run: bool = True) -> Dict[str, Any]:
        """Bir skill'i küçültür.

        Parametreler:
            sisli: ``sisbul()``'dan dönen skill sözlüÄŸü.
            dry_run: True ise iÅŸlem yapmaz, sadece raporlar.

        DönüÅŸ: Ä°ÅŸlem raporu.
        """
        rapor: Dict[str, Any] = {
            "ad": sisli["ad"],
            "yol": str(sisli["yol"]),
            "dry_run": dry_run,
            "adimlar": [],
            "basari": False,
            "onceki_boyut": 0,
            "sonraki_boyut": 0,
            "hata": None,
        }

        try:
            icerik = sisli["icerik"]
            rapor["onceki_boyut"] = len(icerik.encode("utf-8"))
            referans_parcalar: List[str] = []

            # 1. References bölümlerini ayÄ±r
            if sisli.get("references_bolumleri"):
                for ref in sisli["references_bolumleri"]:
                    parca = icerik[ref["baslangic"] : ref["bitis"]]
                    referans_parcalar.append(parca)
                    icerik = icerik[: ref["baslangic"]] + icerik[ref["bitis"] :]
                rapor["adimlar"].append(
                    f"references bölümleri ayrÄ±ldÄ± ({len(referans_parcalar)} parça)"
                )

            # 2. Frontmatter temizliÄŸi
            yeni_icerik, cikarilan_fm = _trim_asiri_frontmatter(icerik)
            if cikarilan_fm:
                icerik = yeni_icerik
                rapor["adimlar"].append(
                    f"frontmatter kÄ±saltÄ±ldÄ± ({len(cikarilan_fm)} alan)"
                )

            # 3. Kod örneklerini kÄ±salt
            yeni_icerik, cikarilan_kod = _trim_kod_ornekleri(icerik)
            if cikarilan_kod:
                icerik = yeni_icerik
                rapor["adimlar"].append(
                    f"kod örnekleri kÄ±saltÄ±ldÄ± ({len(cikarilan_kod)} blok)"
                )
                for k in cikarilan_kod:
                    referans_parcalar.append(k)

            # 4. Gereksiz açÄ±klamalarÄ± kÄ±salt
            yeni_icerik = _trim_gereksiz_aciklamalar(icerik)
            if len(yeni_icerik) < len(icerik):
                icerik = yeni_icerik
                rapor["adimlar"].append(
                    f"açÄ±klamalar kÄ±saltÄ±ldÄ± ({len(icerik.encode('utf-8'))} -> {len(yeni_icerik.encode('utf-8'))})"
                )

            # 5. Listeleri kÄ±salt
            yeni_icerik = _trim_asiri_listeler(icerik)
            if len(yeni_icerik) < len(icerik):
                icerik = yeni_icerik
                rapor["adimlar"].append("listeler kÄ±saltÄ±ldÄ±")

            rapor["sonraki_boyut"] = len(icerik.encode("utf-8"))

            # Uygulama
            if not dry_run:
                # Ana skill dosyasÄ±nÄ± güncelle
                sisli["yol"].write_text(icerik, encoding="utf-8")

                # References klasörü
                if referans_parcalar:
                    ref_dizini = sisli["yol"].parent / "references"
                    ref_dizini.mkdir(parents=True, exist_ok=True)
                    for i, parc in enumerate(referans_parcalar):
                        ref_dosya = ref_dizini / f"{sisli['yol'].stem}_ref_{i+1}.md"
                        ref_dosya.write_text(parc, encoding="utf-8")
                    rapor["adimlar"].append(
                        f"references/ klasörü oluÅŸturuldu ({len(referans_parcalar)} dosya)"
                    )

            rapor["basari"] = True

        except Exception as e:
            rapor["hata"] = str(e)

        return rapor

    def shrink_all(
        self, skills: List[Dict[str, Any]], dry_run: bool = True
    ) -> List[Dict[str, Any]]:
        """Tüm ÅŸiÅŸkin skill'leri küçültür."""
        raporlar = []
        for s in skills:
            r = self.shrink(s, dry_run=dry_run)
            raporlar.append(r)
        return raporlar

    def istatistik(self) -> Dict[str, Any]:
        """Skill deposu istatistikleri."""
        if not self._tum_skills:
            self.tara()

        toplam = len(self._tum_skills)
        sisli = self.sisbul(self._tum_skills)

        # Kategori bazÄ±nda
        kat_dagitim: Dict[str, int] = {}
        for s in self._tum_skills:
            kat = s.get("kategori", "genel")
            kat_dagitim[kat] = kat_dagitim.get(kat, 0) + 1

        # Boyut daÄŸÄ±lÄ±mÄ±
        boyut_kategorileri = {
            "10KB+": 0,
            "5-10KB": 0,
            "1-5KB": 0,
            "1KB-": 0,
        }
        for s in self._tum_skills:
            b = s["boyut"]
            if b >= 10 * 1024:
                boyut_kategorileri["10KB+"] += 1
            elif b >= 5 * 1024:
                boyut_kategorileri["5-10KB"] += 1
            elif b >= 1024:
                boyut_kategorileri["1-5KB"] += 1
            else:
                boyut_kategorileri["1KB-"] += 1

        top_boyut = sum(s["boyut"] for s in self._tum_skills)
        avg_boyut = int(top_boyut / toplam) if toplam else 0

        return {
            "toplam_skill": toplam,
            "sisli_skill": len(sisli),
            "sisli_oran": f"{len(sisli) * 100 / max(toplam, 1):.1f}%",
            "toplam_boyut": _bytes_insan(top_boyut),
            "ortalama_boyut": _bytes_insan(avg_boyut),
            "kategori_dagilimi": kat_dagitim,
            "boyut_dagilimi": boyut_kategorileri,
            "sisli_detay": [
                {
                    "ad": s["ad"],
                    "boyut": _bytes_insan(s["boyut"]),
                    "satir": s["satir"],
                    "neden": s.get("neden", []),
                    "sis_bulgu_sayisi": len(s.get("siskinlik_bulgulari", [])),
                    "ref_bolum_sayisi": len(s.get("references_bolumleri", [])),
                    "yol": str(s["yol"].relative_to(s["yol"].anchor))
                    if s.get("yol")
                    else "?",
                }
                for s in sisli
            ],
        }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CLI Entry Point
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def cmd_skill_shrink(args) -> int:
    """`reymen skill shrink` CLI komutu.

    Parametreler (argparse Namespace):
        dry_run: --dry-run flag
        apply: --apply flag
        stats: --stats flag
    """
    proje_kok = Path(__file__).parent.parent.parent.parent.resolve()

    # Skill dizinleri
    skills_dizinleri = [
        proje_kok / "skills",
    ]

    # cereyan/skills varsa ekle
    cereyan_skills = proje_kok / "src" / "reymen" / "cereyan" / "skills"
    if cereyan_skills.exists():
        skills_dizinleri.append(cereyan_skills)

    shrink = SkillShrink(skills_dizinleri)

    # â”€â”€ --stats â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if getattr(args, "stats", False):
        ist = shrink.istatistik()
        print(f"\n  {_c('Skill Deposu Ä°statistikleri')}")
        print(f"  {_d('â”€' * 50)}")
        print(f"  Toplam skill:      {_g(ist['toplam_skill'])}")
        print(f"  ÅiÅŸkin skill:      {_y(ist['sisli_skill'])} ({ist['sisli_oran']})")
        print(f"  Toplam boyut:      {_d(ist['toplam_boyut'])}")
        print(f"  Ortalama boyut:    {_d(ist['ortalama_boyut'])}")
        print(f"\n  {_c('Boyut DaÄŸÄ±lÄ±mÄ±')}")
        for kat, sayi in sorted(ist["boyut_dagilimi"].items()):
            bar = "â–ˆ" * min(sayi, 20) + "â–’" * max(0, 20 - min(sayi, 20))
            print(f"    {_d(kat+':')} {_g(str(sayi)):>4}  {bar}")
        print(f"\n  {_c('Kategori DaÄŸÄ±lÄ±mÄ±')}")
        for kat, sayi in sorted(ist["kategori_dagilimi"].items()):
            print(f"    {_d(kat+':')} {sayi}")
        print()
        return 0

    # â”€â”€ Normal tarama + shrink â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print(f"\n  {_c('Skill Küçültme TaramasÄ±')}")
    print(f"  {_d('â”€' * 50)}")

    tum = shrink.tara()
    print(f"  Toplam skill: {_g(len(tum))}")

    sisli = shrink.sisbul(tum)
    print(f"  ÅiÅŸkin skill: {_y(len(sisli))}")
    print()

    dry_run = getattr(args, "dry_run", True)  # VarsayÄ±lan dry-run
    apply = getattr(args, "apply", False)
    if apply:
        dry_run = False

    if not sisli:
        print(f"  {_g('âœ“')} ÅiÅŸkin skill bulunamadÄ±, her ÅŸey temiz!")
        print()
        return 0

    # Skill listesi
    for i, s in enumerate(sisli, 1):
        print(f"  {_c(f'#{i}')} {_g(s['ad'])}")
        print(f"    Yol:    {_d(str(s['yol']))}")
        print(
            f"    Boyut:  {_y(_bytes_insan(s['boyut']))} / {_y(str(s['satir']))} satÄ±r"
        )
        print(f"    Neden:  {', '.join(s['neden'])}")
        if s["toplam_sis_boyut"] > 0:
            print(
                f"    ÅiÅŸkin: {_r(_bytes_insan(s['toplam_sis_boyut']))} tespit edildi"
            )
        if s["references_bolumleri"]:
            print(
                f"    Ref:    {_b(str(len(s['references_bolumleri'])) + ' bölüm taÅŸÄ±nabilir')}"
            )
        print()

    if dry_run:
        print(f"  {_y('â„¹')} Dry-run modu â€” hiçbir deÄŸiÅŸiklik yapÄ±lmadÄ±.")
        print(f"  {_d('Uygulamak için:')} {_g('reymen skill shrink --apply')}")
        print()
        return 0

    # â”€â”€ Apply â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    print(f"  {_c('Küçültme UygulanÄ±yor...')}")
    print(f"  {_d('â”€' * 50)}")

    raporlar = shrink.shrink_all(sisli, dry_run=False)

    basarili = 0
    basarisiz = 0
    toplam_tasarruf = 0

    for r in raporlar:
        if r["basari"]:
            basarili += 1
            kazanc = r["onceki_boyut"] - r["sonraki_boyut"]
            toplam_tasarruf += kazanc
            print(
                f"  {_g('âœ“')} {r['ad']}: {_bytes_insan(r['onceki_boyut'])} â†’ {_bytes_insan(r['sonraki_boyut'])} ({_g(_bytes_insan(kazanc))} tasarruf)"
            )
            for a in r["adimlar"]:
                print(f"    {_d('â†’')} {a}")
        else:
            basarisiz += 1
            print(f"  {_r('âœ—')} {r['ad']}: HATA - {r['hata']}")

    print(f"\n  {_d('â”€' * 50)}")
    print(f"  {_g(f'âœ“ {basarili}')} skill küçültüldü, {_r(f'{basarisiz}')} hata")
    print(f"  Toplam tasarruf: {_g(_bytes_insan(toplam_tasarruf))}")
    print()

    return 0 if basarisiz == 0 else 1
