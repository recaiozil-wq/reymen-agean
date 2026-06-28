"""
otonom-gece-gelistirme: Fark Analizi Scripti

ReYMeN SKILL.md dosyaları ile Obsidian skill notlarını karşılaştırır.
İsim çakışmalarını tespit eder (ReYMeN audiocraft = Obsidian audiocraft-audio-generation vb.)
Temiz (shared/ReYMeN-only/obsidian-only) rapor üretir.

Kullanım:
  python scripts/diff_analysis.py

Output format (JSON):
  {
    "shared": ["skill1", "skill2", ...],
    "ReYMeN_only": ["skillA", ...],
    "obsidian_only": ["notX.md", ...],
    "isim_cakismalari": [{"ReYMeN": "audiocraft", "obsidian": "audiocraft-audio-generation"}, ...],
    "summary": {
      "ReYMeN_count": 142,
      "obsidian_count": 156,
      "shared": 133,
      "ReYMeN_only": 8,
      "obsidian_only": 13,
      "isim_cakismalari": 9
    }
  }
"""

import os, re, json
from pathlib import Path

# === PATHS ===
ReYMeN_SKILLS = Path(r"C:\Users\marko\AppData\Local\ReYMeN\skills")
OBSIDIAN_SKILLS = Path(r"C:\Users\marko\OneDrive\Belgeler\Obsidian Vault\ReYMeN\Skills")

# === KNOWN NAME ALIASES (ReYMeN adı -> Obsidian ad(lar)ı) ===
# Sync scripti YAML frontmatter'daki skill_name ile eşleşir, dosya adı farkını tolere eder.
# Bu liste sadece raporlama amaçlıdır.
NAME_ALIASES = {
    "audiocraft": {"obsidian_names": ["audiocraft-audio-generation"]},
    "creative-ideation": {"obsidian_names": ["ideation"]},
    "lm-evaluation-harness": {"obsidian_names": ["evaluating-llms-harness"]},
    "notion-research": {"obsidian_names": ["notion-research-documentation"]},
    "openai-pdf": {"obsidian_names": ["pdf"]},
    "playwright-browser": {"obsidian_names": ["playwright"]},
    "segment-anything": {"obsidian_names": ["segment-anything-model"]},
    "vllm": {"obsidian_names": ["serving-llms-vllm"]},
    "openai-screenshot": {"obsidian_names": ["screenshot"]},
    "windows-keyboard-shortcuts": {"obsidian_names": [
        "windows-shortcuts-gelistirici",
        "windows-shortcuts-metin-pano",
        "windows-shortcuts-sistem-pencere",
        "windows-shortcuts-tarayici-dosya",
    ]},
}


def normalize(name: str) -> str:
    """Basitleştirilmiş normalizasyon: lowercase, tire/altçizgi sil, boşlukları tire yap."""
    return re.sub(r"[_-]", "", name.strip().lower().replace(" ", "-"))


def get_ReYMeN_skills() -> dict[str, str]:
    """ReYMeN skills dizinini tara, {normalized_name: real_name} sözlüğü döndür."""
    skills = {}
    for skill_md in sorted(ReYMeN_SKILLS.rglob("SKILL.md")):
        rel = skill_md.relative_to(ReYMeN_SKILLS)
        parts = rel.parts
        # İlk klasör adı skill adıdır (kategori/skill-adi/SKILL.md)
        # Bazıları direkt skills/skill-adi/SKILL.md, bazıları skills/kategori/skill-adi/SKILL.md
        if len(parts) >= 2:
            skill_name = parts[-2]  # skill-adi
        else:
            skill_name = parts[0].replace("SKILL.md", "").strip("/")

        # __cleanup_* ve ___cleanup_* klasörlerini atla
        if "__cleanup" in skill_name or "___cleanup" in skill_name:
            continue
        # .obsolete dosyalarını atla
        if ".obsolete" in skill_name:
            continue

        skills[normalize(skill_name)] = skill_name

    return skills


def get_obsidian_notes() -> dict[str, str]:
    """Obsidian Skills dizinini tara, {normalized_name: real_name} sözlüğü döndür."""
    notes = {}
    for note_path in sorted(OBSIDIAN_SKILLS.rglob("*.md")):
        name = note_path.stem
        # _ ile başlayan index dosyalarını atla
        if name.startswith("_"):
            continue
        notes[normalize(name)] = name
    return notes


def main():
    ReYMeN = get_ReYMeN_skills()
    obsidian = get_obsidian_notes()

    ReYMeN_norm = set(ReYMeN.keys())
    obsidian_norm = set(obsidian.keys())

    shared_norm = ReYMeN_norm & obsidian_norm
    ReYMeN_only_norm = ReYMeN_norm - obsidian_norm
    obsidian_only_norm = obsidian_norm - ReYMeN_norm

    # Normalden gerçek isimlere çevir
    shared = sorted(ReYMeN[n] for n in shared_norm)
    ReYMeN_only = sorted(ReYMeN[n] for n in ReYMeN_only_norm)
    obsidian_only = sorted(obsidian[n] for n in obsidian_only_norm)

    # İsim çakışmaları: NAME_ALIASES'teki eşleşmeleri kontrol et
    isim_cakismalari = []
    for ReYMeN_name, alias_info in NAME_ALIASES.items():
        ReYMeN_norm_name = normalize(ReYMeN_name)
        if ReYMeN_norm_name not in ReYMeN_norm:
            continue
        for obsidian_alias in alias_info["obsidian_names"]:
            if normalize(obsidian_alias) in obsidian_norm:
                isim_cakismalari.append({
                    "ReYMeN": ReYMeN_name,
                    "obsidian": obsidian_alias,
                })

    result = {
        "shared": shared,
        "ReYMeN_only": ReYMeN_only,
        "obsidian_only": obsidian_only,
        "isim_cakismalari": isim_cakismalari,
        "summary": {
            "ReYMeN_count": len(ReYMeN),
            "obsidian_count": len(obsidian),
            "shared": len(shared),
            "ReYMeN_only": len(ReYMeN_only),
            "obsidian_only": len(obsidian_only),
            "isim_cakismalari": len(isim_cakismalari),
        },
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
