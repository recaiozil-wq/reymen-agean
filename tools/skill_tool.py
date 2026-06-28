# -*- coding: utf-8 -*-
"""skill_tool.py — Skill goruntuleme ve listeleme."""

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".ReYMeN" / "skills"


def run(eylem: str = "liste", ad: str = "") -> str:
    eylem = eylem.strip().lower()

    if eylem == "liste":
        if not SKILLS_DIR.exists():
            return "[Yok] skills/ klasoru bulunamadi."
        # rglob generator'ı list'e al — iki kez iterate için zorunlu
        skills = sorted(SKILLS_DIR.rglob("*.md"))
        if not skills:
            return "[Bilgi] Skill bulunamadi."
        satirlar = [f"Skill ({len(skills)}):"]
        for s in skills[:50]:
            rel = s.relative_to(SKILLS_DIR)
            satirlar.append(f"  - {rel}")
        return "\n".join(satirlar)

    if eylem == "goruntule":
        if not ad:
            return "[Hata]: ad parametresi gerekli."
        # Önce doğrudan dene
        hedef = SKILLS_DIR / f"{ad}.md"
        if not hedef.exists():
            # Recursive ara — generator tükenmiyor, ilk eşleşmeyi al
            eslesme = next(SKILLS_DIR.rglob(f"{ad}.md"), None)
            if eslesme is None:
                return f"[Hata]: '{ad}' skill bulunamadi."
            hedef = eslesme
        return hedef.read_text(encoding="utf-8")

    return f"[Hata]: eylem 'liste' veya 'goruntule' olmali, alindi: '{eylem}'"


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("SKILL", run, "Skill listele/goruntule")
