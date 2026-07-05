# -*- coding: utf-8 -*-
"""
skill_hub.py â€” ReYMeN Skill Hub. Ice/disa aktarma, yedekleme.
"""

from __future__ import annotations

import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

_PROJE_KOK = Path(__file__).resolve().parent.parent.parent.parent
_SKILLS_DIR = _PROJE_KOK / "skills"
_HUB_DIR = _PROJE_KOK / "skill_hub_exports"


def _skills_listele() -> List[dict]:
    """Tum skill'leri metadata ile listele."""
    sonuc = []
    if not _SKILLS_DIR.exists():
        return sonuc
    for f in sorted(_SKILLS_DIR.iterdir()):
        if f.is_dir() and (f / "SKILL.md").exists():
            meta = _skill_metadata_oku(f / "SKILL.md")
            meta["klasor"] = f.name
            sonuc.append(meta)
        elif f.suffix == ".md":
            meta = _skill_metadata_oku(f)
            meta["klasor"] = f.stem
            meta["dosya"] = f.name
            sonuc.append(meta)
    return sonuc


def _skill_metadata_oku(yol: Path) -> dict:
    """SKILL.md (veya .md) dosyasindan YAML frontmatter oku."""
    try:
        icerik = yol.read_text(encoding="utf-8")
    except Exception:
        return {"name": yol.stem, "description": "", "category": ""}

    # YAML frontmatter ayikla (--- ... ---)
    meta = {"name": yol.stem, "description": "", "category": ""}
    if icerik.startswith("---"):
        try:
            import yaml
            _, fm, _ = icerik.split("---", 2)
            fm_data = yaml.safe_load(fm)
            if isinstance(fm_data, dict):
                meta.update({k: v for k, v in fm_data.items() if k in meta})
        except Exception:
            pass
    return meta


def export_skills(hedef_zip: Optional[str] = None) -> str:
    """Tum skill'leri ZIP olarak disa aktar."""
    skills = _skills_listele()
    if not skills:
        return "Hic skill bulunamadi."

    if not hedef_zip:
        _HUB_DIR.mkdir(parents=True, exist_ok=True)
        tarih = datetime.now().strftime("%Y%m%d_%H%M%S")
        hedef_zip = str(_HUB_DIR / f"skills_export_{tarih}.zip")

    with zipfile.ZipFile(hedef_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for skill in skills:
            kaynak = _SKILLS_DIR / skill.get("klasor", skill["name"])
            if kaynak.is_dir():
                for root, dirs, files in os.walk(kaynak):
                    for f in files:
                        dosya_yol = Path(root) / f
                        zf.write(dosya_yol, dosya_yol.relative_to(_SKILLS_DIR))
            elif kaynak.with_suffix(".md").exists():
                zf.write(kaynak.with_suffix(".md"), kaynak.with_suffix(".md").name)

    return f"Export basarili: {hedef_zip} ({len(skills)} skill)"


def import_skills(kaynak_zip: str, override: bool = False) -> str:
    """ZIP'den skill iceri aktar."""
    kaynak = Path(kaynak_zip)
    if not kaynak.exists():
        return f"Dosya bulunamadi: {kaynak_zip}"

    sayac = 0
    with zipfile.ZipFile(kaynak, "r") as zf:
        for name in zf.namelist():
            hedef = _SKILLS_DIR / name
            if hedef.exists() and not override:
                continue
            hedef.parent.mkdir(parents=True, exist_ok=True)
            zf.extract(name, _SKILLS_DIR)
            sayac += 1

    return f"Import basarili: {sayac} dosya iceri aktarildi."


def hub_listele() -> str:
    """Skill'leri listele (konsol icin)."""
    skills = _skills_listele()
    if not skills:
        return "Skill hub'da hic skill yok."

    satirlar = [f"Skill Hub: {len(skills)} skill"]
    for s in skills[:20]:
        satirlar.append(f"  - {s['name']:30s} | {s['description'][:50]}")
    if len(skills) > 20:
        satirlar.append(f"  ... ve {len(skills) - 20} skill daha")
    return "\n".join(satirlar)


def hub_durum() -> dict:
    """Skill hub durumu (programatik kullanim icin)."""
    skills = _skills_listele()
    return {
        "toplam_skill": len(skills),
        "skills_dir": str(_SKILLS_DIR),
        "exports_dir": str(_HUB_DIR),
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "export":
            print(export_skills(sys.argv[2] if len(sys.argv) > 2 else None))
        elif sys.argv[1] == "import":
            if len(sys.argv) > 2:
                print(import_skills(sys.argv[2]))
            else:
                print("Kullanim: python skill_hub.py import <dosya.zip>")
        elif sys.argv[1] == "list":
            print(hub_listele())
        elif sys.argv[1] == "status":
            print(json.dumps(hub_durum(), ensure_ascii=False, indent=2))
    else:
        print(hub_listele())
