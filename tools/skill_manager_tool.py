# -*- coding: utf-8 -*-
"""skill_manager_tool.py — Skill Yonetim Araci.

Skill'leri listele, ara, ekle, cikar ve detaylarini goster.
"""

from pathlib import Path

SKILLS_KLASOR = Path(__file__).parent.parent / ".ReYMeN" / "skills"


def skill_listele(kategori: str = "") -> str:
    """Skill'leri listele.

    Args:
        kategori: Bos = tumu, dolu = sadece o kategori

    Returns:
        Skill listesi
    """
    if not SKILLS_KLASOR.exists():
        return "[Skill]: Skills klasoru bulunamadi."

    if kategori:
        k_klasor = SKILLS_KLASOR / kategori
        if not k_klasor.exists():
            return f"[Skill]: '{kategori}' kategorisi bulunamadi."
        dosyalar = list(k_klasor.rglob("SKILL.md"))
    else:
        dosyalar = list(SKILLS_KLASOR.rglob("SKILL.md"))

    if not dosyalar:
        return "[Skill]: Skill bulunamadi."

    kategoriler = {}
    for d in dosyalar:
        kat = d.parent.parent.name if d.parent.parent != SKILLS_KLASOR else d.parent.name
        kategoriler.setdefault(kat, []).append(d.parent.name)

    satirlar = [f"[Skill] Toplam {len(dosyalar)} skill:\n"]
    for kat, skiller in sorted(kategoriler.items()):
        satirlar.append(f"  {kat}/ ({len(skiller)} skill)")
        for s in skiller[:5]:
            satirlar.append(f"    - {s}")
        if len(skiller) > 5:
            satirlar.append(f"    ... ve {len(skiller)-5} daha")
    return "\n".join(satirlar)


def skill_ara(sorgu: str) -> str:
    """Skill icinde metin ara.

    Args:
        sorgu: Aranacak metin

    Returns:
        Eslesen skill'ler
    """
    if not SKILLS_KLASOR.exists():
        return "[Skill]: Skills klasoru bulunamadi."

    eslesen = []
    for dosya in SKILLS_KLASOR.rglob("SKILL.md"):
        icerik = dosya.read_text(encoding="utf-8")
        if sorgu.lower() in icerik.lower():
            eslesen.append(f"  {dosya.parent.parent.name}/{dosya.parent.name}")

    if not eslesen:
        return f"[Skill]: '{sorgu}' ile ilgili skill bulunamadi."
    return "[Skill Arama]:\n" + "\n".join(eslesen[:10])


def skill_detay(ad: str) -> str:
    """Bir skill'in detayini goster.

    Args:
        ad: Skill adi (klasor adi)

    Returns:
        Skill icerigi
    """
    for dosya in SKILLS_KLASOR.rglob(f"**/{ad}/SKILL.md"):
        return dosya.read_text(encoding="utf-8")
    return f"[Skill]: '{ad}' bulunamadi."


def skill_sayisi() -> int:
    """Toplam SKILL.md sayisini dondur."""
    if not SKILLS_KLASOR.exists():
        return 0
    return len(list(SKILLS_KLASOR.rglob("SKILL.md")))


if __name__ == "__main__":
    print(skill_listele()[:500])
