"""ReYMeN skill'lerini ReYMeN formatÄ±na dÃ¶nÃ¼ÅŸtÃ¼r.
KullanÄ±m: python reymen/scripts/skill_import.py [--kategori AI_ML,DevOps]

ReYMeN: ~/AppData/Local/reymen/skills/<kategori>/<skill>/SKILL.md
ReYMeN: reymen/cereyan/skills/Skiller/<kategori>/<skill>_SKILL.md (dÃ¼z dosya)
"""

import os, re, shutil
from pathlib import Path

REYMEN_SKILLS = Path(__file__).parent.parent / "cereyan/skills/Skiller"

# Kategori eÅŸleme: ReYMeN â†’ ReYMeN
KATEGORI_MAP = {
    "devops": "DevOps",
    "data-science": "AI_ML",
    "mlops": "AI_ML",
    "mlops/inference": "AI_ML",
    "mlops/evaluation": "AI_ML",
    "mlops/models": "AI_ML",
    "mlops/research": "AI_ML",
    "software-development": "Yazilim",
    "software": "Yazilim",
    "security": "Guvenlik",
    "kali-pentest": "Guvenlik",
    "windows-automation": "Windows",
    "windows": "Windows",
    "productivity": "Verimlilik",
    "note-taking": "Verimlilik",
    "creative": "Medya",
    "media": "Medya",
    "gaming": "Medya",
    "github": "DevOps",
    "mcp": "MCP",
    "autonomous-ai-agents": "AI_ML",
    "user-preferences": "Kullanici",
    "workflow": "Surec",
    "user-preferences/hersona/skills": "Kullanici",
}


def skill_aktar(hedef_klasor: str = "", limit: int = 0):
    """ReYMeN skill'lerini ReYMeN formatÄ±na Ã§evir."""
    hedef = REYMEN_SKILLS
    if hedef_klasor:
        hedef = hedef / hedef_klasor
    hedef.mkdir(parents=True, exist_ok=True)

    aktarilan = 0
    for kategori_dizini in sorted(REYMEN_SKILLS.iterdir()):
        if not kategori_dizini.is_dir():
            continue

        # Kategori eÅŸle
        reymen_kat = KATEGORI_MAP.get(kategori_dizini.name, "Diger")
        if hedef_klasor and reymen_kat != hedef_klasor:
            continue

        for skill_dizini in sorted(kategori_dizini.iterdir()):
            skill_md = skill_dizini / "SKILL.md"
            if not skill_md.exists():
                continue

            # ReYMeN formatÄ±: <kategori>/<skill>/SKILL.md
            # ReYMeN formatÄ±: <kategori>/<skill>_SKILL.md (dÃ¼z dosya)
            icerik = skill_md.read_text("utf-8", errors="replace")

            # Frontmatter'Ä± temizle (ReYMeN formatÄ±na uygun)
            icerik = re.sub(
                r"^---\n.*?\n---\n", "", icerik, flags=re.DOTALL | re.MULTILINE
            )
            icerik = icerik.strip()

            # Dosya adÄ±: "skill_adi_SKILL.md"
            dosya_adi = f"{skill_dizini.name}_SKILL.md"
            hedef_klasor_path = hedef / reymen_kat
            hedef_klasor_path.mkdir(parents=True, exist_ok=True)
            (hedef_klasor_path / dosya_adi).write_text(icerik, "utf-8")

            aktarilan += 1
            if limit and aktarilan >= limit:
                return aktarilan

    return aktarilan


def skill_say():
    """ReYMeN ve ReYMeN'deki skill sayÄ±larÄ±nÄ± gÃ¶ster."""
    ReYMeN = sum(
        1
        for k in REYMEN_SKILLS.iterdir()
        if k.is_dir()
        for s in k.iterdir()
        if (s / "SKILL.md").exists()
    )
    reymen = sum(1 for f in REYMEN_SKILLS.rglob("*_SKILL.md"))
    return {"ReYMeN": ReYMeN, "reymen": reymen, "eksik": ReYMeN - reymen}


if __name__ == "__main__":
    import sys

    hedef = sys.argv[1] if len(sys.argv) > 1 else ""
    lim = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    once = skill_say()
    print(f"ReYMeN skill: {once['ReYMeN']} | ReYMeN skill: {once['reymen']}")

    adet = skill_aktar(hedef, lim)
    sonra = skill_say()

    print(f"Aktarilan: {adet} skill")
    print(f"ReYMeN toplam: {sonra['reymen']} (Ã¶nce: {once['reymen']})")
    print(f"Hala eksik: {sonra['eksik']}")
