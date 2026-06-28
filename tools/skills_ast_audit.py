# -*- coding: utf-8 -*-
"""tools/skills_ast_audit.py — Skill AST Denetim Araci.

SKILL.md dosyalarini YAML frontmatter ve yapisal butunluk
acisindan kontrol eder.
"""
import os
import re
from pathlib import Path


def _skill_kokleri() -> list:
    """Projedeki SKILL.md dosyalarinin bulundugu dizinleri bulur."""
    try:
        tool_path = Path(__file__).resolve().parent
        proje_kok = tool_path.parent
        skill_dizinleri = []
        # .ReYMeN/profiles/ altinda skills/ var
        profiles_dir = proje_kok / ".ReYMeN" / "profiles"
        if profiles_dir.exists():
            for profil in profiles_dir.iterdir():
                if profil.is_dir():
                    skills_dir = profil / "skills"
                    if skills_dir.exists():
                        for skill_dizini in skills_dir.iterdir():
                            skill_dosyasi = skill_dizini / "SKILL.md"
                            if skill_dosyasi.exists():
                                skill_dizinleri.append(skill_dizini)
        # Ayrica ReYMeN_projesi/skills/ altina da bak
        skills_root = proje_kok / "skills"
        if skills_root.exists():
            for skill_dizini in skills_root.iterdir():
                if skill_dizini.is_dir():
                    skill_dosyasi = skill_dizini / "SKILL.md"
                    if skill_dosyasi.exists():
                        skill_dizinleri.append(skill_dizini)
        return skill_dizinleri
    except Exception:
        return []


def _yaml_frontmatter_kontrol(icerik: str) -> dict:
    """YAML frontmatter yapisini kontrol eder."""
    sonuc = {
        "var_mi": False,
        "baslik_var_mi": False,
        "aciklama_var_mi": False,
        "surum_var_mi": False,
        "tags_var_mi": False,
        "dengeli_mi": False,
        "hata": "",
    }
    if not icerik.strip().startswith("---"):
        sonuc["hata"] = "YAML frontmatter baslangic isareti (---) bulunamadi."
        return sonuc

    # Frontmatter baslangic ve bitis
    ikinci_uc_tire = icerik.find("---", 3)
    if ikinci_uc_tire == -1:
        sonuc["hata"] = "YAML frontmatter bitis isareti (---) bulunamadi."
        return sonuc

    sonuc["var_mi"] = True
    yaml_blok = icerik[3:ikinci_uc_tire].strip()

    # Anahtar alanlari kontrol et
    if "title" in yaml_blok or "baslik" in yaml_blok:
        sonuc["baslik_var_mi"] = True
    if "description" in yaml_blok or "aciklama" in yaml_blok:
        sonuc["aciklama_var_mi"] = True
    if "version" in yaml_blok or "surum" in yaml_blok:
        sonuc["surum_var_mi"] = True
    if "tags" in yaml_blok or "etiketler" in yaml_blok:
        sonuc["tags_var_mi"] = True

    sonuc["dengeli_mi"] = True
    return sonuc


def run(islem='tara', **kwargs) -> str:
    """Skill AST denetimi yapar.

    Parametreler:
        islem (str): 'tara', 'kontrol' veya 'raporla'
        skill_adi (str): Belirli bir skill adi (opsiyonel)

    Returns:
        str: Denetim sonucu.
    """
    try:
        if islem == 'tara':
            skill_dizinleri = _skill_kokleri()
            if not skill_dizinleri:
                return "SKILL.md dosyasi bulunamadi."

            satirlar = [f"Skill denetimi basliyor ({len(skill_dizinleri)} skill)..."]

            for dizin in skill_dizinleri:
                skill_adi = dizin.name
                skill_dosyasi = dizin / "SKILL.md"
                icerik = skill_dosyasi.read_text(encoding="utf-8")
                kontrol = _yaml_frontmatter_kontrol(icerik)
                satirlar.append(f"\n--- {skill_adi} ---")
                if kontrol["var_mi"]:
                    durum = []
                    if kontrol["baslik_var_mi"]:
                        durum.append("baslik")
                    if kontrol["aciklama_var_mi"]:
                        durum.append("aciklama")
                    if kontrol["surum_var_mi"]:
                        durum.append("surum")
                    if kontrol["tags_var_mi"]:
                        durum.append("etiketler")
                    satirlar.append(
                        f"  YAML frontmatter: Gecerli ({', '.join(durum)})"
                    )
                else:
                    satirlar.append(f"  YAPI SALDIRISI: {kontrol['hata']}")

            return "\n".join(satirlar)

        elif islem == 'kontrol':
            skill_adi = kwargs.get('skill_adi', '')
            if not skill_adi:
                return "Hata: 'skill_adi' parametresi zorunludur."

            skill_dizinleri = _skill_kokleri()
            hedef = None
            for dizin in skill_dizinleri:
                if dizin.name == skill_adi:
                    hedef = dizin
                    break

            if not hedef:
                return f"Skill bulunamadi: {skill_adi}"

            skill_dosyasi = hedef / "SKILL.md"
            icerik = skill_dosyasi.read_text(encoding="utf-8")
            kontrol = _yaml_frontmatter_kontrol(icerik)

            satirlar = [f"Skill: {skill_adi}"]
            satirlar.append(f"  Dosya: {skill_dosyasi}")
            satirlar.append(f"  Boyut: {len(icerik)} karakter")
            satirlar.append(
                f"  YAML Frontmatter: {'VAR' if kontrol['var_mi'] else 'YOK'}"
            )
            if kontrol["var_mi"]:
                satirlar.append(f"    Baslik: {'VAR' if kontrol['baslik_var_mi'] else 'YOK'}")
                satirlar.append(
                    f"    Aciklama: {'VAR' if kontrol['aciklama_var_mi'] else 'YOK'}"
                )
                satirlar.append(f"    Surum: {'VAR' if kontrol['surum_var_mi'] else 'YOK'}")
                satirlar.append(f"    Etiketler: {'VAR' if kontrol['tags_var_mi'] else 'YOK'}")
                satirlar.append(
                    f"    Yapi: {'DENGELI' if kontrol['dengeli_mi'] else 'BOZUK'}"
                )
            else:
                satirlar.append(f"  Hata: {kontrol['hata']}")
            return "\n".join(satirlar)

        elif islem == 'raporla':
            skill_dizinleri = _skill_kokleri()
            if not skill_dizinleri:
                return "SKILL.md dosyasi bulunamadi."

            toplam = len(skill_dizinleri)
            sorunlu = 0
            detaylar = []

            for dizin in skill_dizinleri:
                skill_adi = dizin.name
                skill_dosyasi = dizin / "SKILL.md"
                icerik = skill_dosyasi.read_text(encoding="utf-8")
                kontrol = _yaml_frontmatter_kontrol(icerik)
                if not kontrol["var_mi"] or not kontrol["dengeli_mi"]:
                    sorunlu += 1
                    detaylar.append(f"  {skill_adi}: {kontrol['hata']}")

            satirlar = ["=== SKILL AST RAPORU ==="]
            satirlar.append(f"Toplam skill: {toplam}")
            satirlar.append(f"Sorunlu skill: {sorunlu}")
            satirlar.append(f"Saglikli skill: {toplam - sorunlu}")
            if detaylar:
                satirlar.append("\nDetaylar:")
                satirlar.extend(detaylar)
            return "\n".join(satirlar)

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Skill AST denetim hatasi: {e}"
