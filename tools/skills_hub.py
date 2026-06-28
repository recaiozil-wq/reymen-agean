# -*- coding: utf-8 -*-
"""skills_hub.py â€” Skill PaylaÅŸÄ±m Merkezi.

.ReYMeN/skills/ klasÃ¶rÃ¼nÃ¼ tarar, skill'leri listeler, kategorilere ayÄ±rÄ±r,
arama yapar. TÃ¼m Ã§Ä±ktÄ±lar JSON formatÄ±ndadÄ±r.
"""

import json
import os
from pathlib import Path
from typing import Optional

# VarsayÄ±lan skills klasÃ¶rÃ¼ (proje kÃ¶kÃ¼ndeki .ReYMeN/skills)
PROJE_KOKU = Path(__file__).parent.parent.resolve()
SKILLS_KLASOR = PROJE_KOKU / ".ReYMeN" / "skills"


def _skills_klasor_bul() -> Path:
    """Skills klasÃ¶rÃ¼nÃ¼n var olduÄŸundan emin ol, yoksa hata fÄ±rlat."""
    if not SKILLS_KLASOR.exists():
        raise FileNotFoundError(
            f"Skills klasÃ¶rÃ¼ bulunamadÄ±: {SKILLS_KLASOR}"
        )
    return SKILLS_KLASOR


def _skill_okunabilir_ol(ad: str) -> Optional[dict]:
    """Bir skill klasÃ¶rÃ¼nÃ¼n SKILL.md iÃ§eriÄŸini oku, dict olarak dÃ¶ndÃ¼r."""
    skill_dosya = SKILLS_KLASOR / ad / "SKILL.md"
    if not skill_dosya.exists():
        return None
    try:
        icerik = skill_dosya.read_text(encoding="utf-8", errors="replace")
    except Exception:
        icerik = ""
    baslik = icerik.split("\n")[0].strip("# \t\r\n") if icerik else ad
    return {
        "ad": ad,
        "baslik": baslik,
        "dosya_yolu": str(skill_dosya.resolve()),
        "icerik_uzunlugu": len(icerik),
    }


def skill_kategorileri() -> str:
    """Mevcut tÃ¼m kategorileri ve her kategorideki skill sayÄ±sÄ±nÄ± dÃ¶ndÃ¼r.

    Returns:
        JSON string: {"kategoriler": [{"kategori": "...", "skill_sayisi": N}, ...]}
    """
    try:
        _skills_klasor_bul()
    except FileNotFoundError as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)

    kategoriler = []
    for entry in sorted(SKILLS_KLASOR.iterdir()):
        if entry.is_dir():
            skill_sayisi = len([
                d for d in entry.iterdir() if d.is_dir() and (d / "SKILL.md").exists()
            ])
            kategoriler.append({
                "kategori": entry.name,
                "skill_sayisi": skill_sayisi,
            })

    return json.dumps({"kategoriler": kategoriler}, ensure_ascii=False, indent=2)


def skill_listele(kategori: Optional[str] = None) -> str:
    """Skill'leri listele, isteÄŸe baÄŸlÄ± kategori filtresiyle.

    Args:
        kategori: None = tÃ¼mÃ¼, string = sadece o kategori

    Returns:
        JSON string
    """
    try:
        _skills_klasor_bul()
    except FileNotFoundError as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)

    sonuc = {"kategori": kategori or "tumu", "skilller": []}

    if kategori:
        kat_klasor = SKILLS_KLASOR / kategori
        if not kat_klasor.exists() or not kat_klasor.is_dir():
            return json.dumps(
                {"hata": f"'{kategori}' kategorisi bulunamadÄ±."},
                ensure_ascii=False,
            )
        skill_klasorleri = [
            d for d in kat_klasor.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        ]
        for sk in sorted(skill_klasorleri):
            bilgi = _skill_okunabilir_ol(sk.name)
            if bilgi:
                bilgi["kategori"] = kategori
                sonuc["skilller"].append(bilgi)
    else:
        for entry in sorted(SKILLS_KLASOR.iterdir()):
            if entry.is_dir():
                skill_klasorleri = [
                    d for d in entry.iterdir()
                    if d.is_dir() and (d / "SKILL.md").exists()
                ]
                for sk in sorted(skill_klasorleri):
                    bilgi = _skill_okunabilir_ol(sk.name)
                    if bilgi:
                        bilgi["kategori"] = entry.name
                        sonuc["skilller"].append(bilgi)

    sonuc["toplam"] = len(sonuc["skilller"])
    return json.dumps(sonuc, ensure_ascii=False, indent=2)


def skill_ara(anahtar_kelime: str) -> str:
    """Skill iÃ§eriklerinde anahtar kelime ara.

    Args:
        anahtar_kelime: Aranacak metin

    Returns:
        JSON string
    """
    try:
        _skills_klasor_bul()
    except FileNotFoundError as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)

    sonuc = {"anahtar_kelime": anahtar_kelime, "eslesenler": []}
    arama = anahtar_kelime.lower()

    for entry in sorted(SKILLS_KLASOR.iterdir()):
        if not entry.is_dir():
            continue
        kategori = entry.name
        for sk in sorted(entry.iterdir()):
            if not sk.is_dir():
                continue
            skill_dosya = sk / "SKILL.md"
            if not skill_dosya.exists():
                continue
            try:
                icerik = skill_dosya.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if arama in icerik.lower():
                sonuc["eslesenler"].append({
                    "ad": sk.name,
                    "kategori": kategori,
                    "baslik": icerik.split("\n")[0].strip("# \t\r\n") if icerik else sk.name,
                })

    sonuc["toplam"] = len(sonuc["eslesenler"])
    return json.dumps(sonuc, ensure_ascii=False, indent=2)


def skill_bilgi(ad: str) -> str:
    """Belirli bir skill'in detay bilgisini dÃ¶ndÃ¼r.

    Args:
        ad: Skill adÄ± (klasÃ¶r adÄ±)

    Returns:
        JSON string
    """
    try:
        _skills_klasor_bul()
    except FileNotFoundError as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)

    # TÃ¼m kategorilerde ara
    for entry in SKILLS_KLASOR.iterdir():
        if not entry.is_dir():
            continue
        sk_klasor = entry / ad
        if sk_klasor.exists() and sk_klasor.is_dir():
            skill_dosya = sk_klasor / "SKILL.md"
            if not skill_dosya.exists():
                return json.dumps(
                    {"hata": f"'{ad}' skill'inde SKILL.md bulunamadÄ±."},
                    ensure_ascii=False,
                )
            try:
                icerik = skill_dosya.read_text(encoding="utf-8", errors="replace")
            except Exception as e:
                return json.dumps(
                    {"hata": f"SKILL.md okunamadÄ±: {e}"},
                    ensure_ascii=False,
                )
            satirlar = icerik.split("\n")
            return json.dumps({
                "ad": ad,
                "kategori": entry.name,
                "baslik": satirlar[0].strip("# \t\r\n") if satirlar else ad,
                "dosya_yolu": str(skill_dosya.resolve()),
                "satir_sayisi": len(satirlar),
                "icerik": icerik,
            }, ensure_ascii=False, indent=2)

    return json.dumps(
        {"hata": f"'{ad}' skill'i bulunamadÄ±."},
        ensure_ascii=False,
    )


def run(**kwargs) -> str:
    """Ana giriÅŸ noktasÄ± â€” kwargs ile hangi fonksiyonun Ã§aÄŸrÄ±lacaÄŸÄ±nÄ± belirle.

    KullanÄ±m:
        run(islem="kategoriler")
        run(islem="listele", kategori="araclar")
        run(islem="ara", anahtar_kelime="python")
        run(islem="bilgi", ad="my-skill")
    """
    try:
        islem = kwargs.get("islem", "listele")

        if islem == "kategoriler":
            return skill_kategorileri()
        elif islem == "listele":
            return skill_listele(kategori=kwargs.get("kategori"))
        elif islem == "ara":
            anahtar = kwargs.get("anahtar_kelime") or kwargs.get("sorgu")
            if not anahtar:
                return json.dumps(
                    {"hata": "Arama iÃ§in 'anahtar_kelime' parametresi gerekli."},
                    ensure_ascii=False,
                )
            return skill_ara(anahtar)
        elif islem == "bilgi":
            ad = kwargs.get("ad")
            if not ad:
                return json.dumps(
                    {"hata": "Bilgi iÃ§in 'ad' parametresi gerekli."},
                    ensure_ascii=False,
                )
            return skill_bilgi(ad)
        else:
            return json.dumps(
                {"hata": f"Bilinmeyen iÅŸlem: {islem}. Åunlardan biri olmalÄ±: kategoriler, listele, ara, bilgi"},
                ensure_ascii=False,
            )
    except Exception as e:
        return json.dumps({"hata": f"Beklenmeyen hata: {e}"}, ensure_ascii=False)


# --- ReYMeN uyumlu GitHubAuth ve GitHubSource stub'larÄ± ---

class SkillSource:
    """Temel skill kaynaÄŸÄ± â€” ReYMeN uyumluluÄŸu."""

    def list_skills(self):
        return []


class GitHubAuth:
    """GitHub API kimlik doÄŸrulamasÄ± â€” ReYMeN uyumluluk stub'Ä±."""

    def __init__(self, token: Optional[str] = None):
        import os
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def get_headers(self) -> dict:
        if self.token:
            return {"Authorization": f"Bearer {self.token}", "Accept": "application/vnd.github+json"}
        return {"Accept": "application/vnd.github+json"}

    @classmethod
    def from_env(cls) -> "GitHubAuth":
        return cls()

class OptionalSkillSource(SkillSource):
    """Opsiyonel skill kaynagi â€” ReYMeN uyumluluÄŸu stub'i."""

    def __init__(self, source=None):
        self.source = source

    def list_skills(self):
        if self.source:
            return self.source.list_skills()
        return []



class WellKnownSkillSource(SkillSource):
    """Bilinen skill kaynaklari — ReYMeN uyumluluk stubu."""

    def __init__(self, auth=None):
        self.auth = auth

    def list_skills(self):
        return []

class SkillsShSource(SkillSource):
    """skills.sh kaynaÄŸÄ± â€” ReYMeN uyumluluÄŸu stub'Ä±."""

    def __init__(self, auth: "GitHubAuth" = None):
        self.auth = auth or GitHubAuth()

    def list_skills(self):
        return []

    @staticmethod
    def _strip_html(html: str) -> str:
        import re
        return re.sub(r"<[^>]+>", "", html)


class GitHubSource(SkillSource):
    """GitHub'dan skill Ã§eken kaynak â€” ReYMeN uyumluluÄŸu stub'Ä±."""

    def __init__(self, auth: "GitHubAuth" = None, extra_taps=None):
        self.auth = auth or GitHubAuth()
        self.extra_taps = extra_taps or []

    def list_skills(self):
        return []

# --- GitHubAuth ve GitHubSource sonu ---


if __name__ == "__main__":
    # Test
    print("=== Kategoriler ===")
    print(run(islem="kategoriler"))
    print("\n=== TÃ¼m Skill'ler ===")
    print(run(islem="listele"))

class ClawHubSource(SkillSource):
    """ClawHub skill kaynagi - ReYMeN uyumluluk stubu."""

    def __init__(self, auth=None):
        self.auth = auth

    def list_skills(self):
        return []
class ClaudeMarketplaceSource(SkillSource):
    """Claude Marketplace skill kaynagi - ReYMeN uyumluluk stubu."""

    def __init__(self, auth=None):
        self.auth = auth

    def list_skills(self):
        return []
class LobeHubSource(SkillSource):
    """LobeHub skill kaynagi - ReYMeN uyumluluk stubu."""
    def __init__(self, auth=None): self.auth = auth
    def list_skills(self): return []

class LocalSkillSource(SkillSource):
    """Yerel skill kaynagi - ReYMeN uyumluluk stubu."""
    def __init__(self, path=None): self.path = path
    def list_skills(self): return []

class ReYMeNSkillSource(SkillSource):
    """ReYMeN skill kaynagi - ReYMeN uyumluluk stubu."""
    def __init__(self, auth=None): self.auth = auth
    def list_skills(self): return []
class BrowseShSource(SkillSource):
    """BrowseSh skill kaynagi - ReYMeN uyumluluk stubu."""
    def __init__(self, auth=None): self.auth = auth
    def list_skills(self): return []

class ReYMeNIndexSource(SkillSource):
    """ReYMeN index skill kaynagi - ReYMeN uyumluluk stubu."""
    def __init__(self, auth=None): self.auth = auth
    def list_skills(self): return []