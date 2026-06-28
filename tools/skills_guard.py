# -*- coding: utf-8 -*-
"""tools/skills_guard.py — Skill Guvenlik Filtresi.

Skill'lerde tehlikeli kod, sifre, API anahtari taramasi yapar.
"""
import os
import re
from pathlib import Path


# Tehlikeli kod desenleri
TEHLIKELI_KOD = re.compile(
    r"(os\.system|subprocess\.(call|Popen|run)|"
    r"eval\(|exec\(|compile\(|__import__\(|"
    r"pickle\.loads|base64\.(b64decode|decode)|"
    r"socket\.|pty\.spawn)",
    re.IGNORECASE,
)

# API anahtari desenleri
API_ANAHTARI = re.compile(
    r"(?:sk-[a-zA-Z0-9]{20,}|"
    r"ghp_[a-zA-Z0-9]{36,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"xox[bpras]-[a-zA-Z0-9\-]{10,}|"
    r"AIza[0-9A-Za-z\-_]{35}|"
    r"pk\.[a-zA-Z0-9]{30,})",
    re.IGNORECASE,
)

# Sifre desenleri
SIFRE = re.compile(
    r"(?:password|passwd|pwd|sifre|parola|secret|api_key|api_anahtar)"
    r"\s*[=:]\s*['\"][^'\"]{4,}['\"]",
    re.IGNORECASE,
)

# Hassas dosya desenleri
HASSAS_DOSYALAR = re.compile(
    r"(\.env|\.pem|\.key|id_rsa|credentials\.json|"
    r"service_account\.json|token\.json|oauth.*\.json)",
    re.IGNORECASE,
)


def _skill_dosyalari(skill_adi: str = "") -> list:
    """Skill dosyalarinin yolunu bulur."""
    tool_path = Path(__file__).resolve().parent
    proje_kok = tool_path.parent
    dosyalar = []

    arama_dizinleri = []

    # .ReYMeN/profiles/*/skills/ alti
    profiles_dir = proje_kok / ".ReYMeN" / "profiles"
    if profiles_dir.exists():
        for profil in profiles_dir.iterdir():
            if profil.is_dir():
                skills_dir = profil / "skills"
                if skills_dir.exists():
                    if skill_adi:
                        skill_dizini = skills_dir / skill_adi
                        if skill_dizini.exists():
                            arama_dizinleri.append(skill_dizini)
                    else:
                        arama_dizinleri.append(skills_dir)

    # skills/ alti
    skills_root = proje_kok / "skills"
    if skills_root.exists():
        if skill_adi:
            skill_dizini = skills_root / skill_adi
            if skill_dizini.exists():
                arama_dizinleri.append(skill_dizini)
        else:
            arama_dizinleri.append(skills_root)

    for dizin in arama_dizinleri:
        if dizin.is_dir():
            for dosya in dizin.rglob("*"):
                if dosya.is_file() and dosya.suffix in (".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sh"):
                    dosyalar.append(dosya)

    return dosyalar


def _dosyayi_tara(dosya_yolu: Path) -> dict:
    """Bir dosyayi guvenlik acisindan tarar."""
    sonuc = {
        "dosya": str(dosya_yolu),
        "tehlikeli_kod": [],
        "api_anahtari": [],
        "sifre": [],
        "hassas_dosya_adi": False,
        "guvenli": True,
    }

    try:
        icerik = dosya_yolu.read_text(encoding="utf-8", errors="replace")
    except Exception:
        sonuc["guvenli"] = False
        return sonuc

    # Dosya adi kontrolu
    if HASSAS_DOSYALAR.search(dosya_yolu.name):
        sonuc["hassas_dosya_adi"] = True
        sonuc["guvenli"] = False

    # Kod icerigi kontrolu
    for eslesme in TEHLIKELI_KOD.finditer(icerik):
        sonuc["tehlikeli_kod"].append(eslesme.group())
        sonuc["guvenli"] = False

    for eslesme in API_ANAHTARI.finditer(icerik):
        sonuc["api_anahtari"].append(eslesme.group())
        sonuc["guvenli"] = False

    for eslesme in SIFRE.finditer(icerik):
        sonuc["sifre"].append(eslesme.group())
        sonuc["guvenli"] = False

    return sonuc


def run(islem='tara', **kwargs) -> str:
    """Skill guvenlik filtrelemesi yapar.

    Parametreler:
        islem (str): 'tara', 'temizle' veya 'kontrol'
        skill_adi (str): Skill adi (opsiyonel, tum skill'ler taranir)
        dosya_yolu (str): Tek dosya yolu (opsiyonel)

    Returns:
        str: Guvenlik raporu.
    """
    try:
        skill_adi = kwargs.get('skill_adi', '')
        dosya_yolu = kwargs.get('dosya_yolu', '')

        if islem == 'tara':
            if dosya_yolu:
                # Tek dosya tara
                dosya = Path(dosya_yolu)
                if not dosya.exists():
                    return f"Dosya bulunamadi: {dosya_yolu}"
                sonuc = _dosyayi_tara(dosya)
                return _sonucu_goster([sonuc])

            # Skill dosyalarini tara
            dosyalar = _skill_dosyalari(skill_adi)
            if not dosyalar:
                if skill_adi:
                    return f"Skill bulunamadi: {skill_adi}"
                return "Skill dosyasi bulunamadi."

            sonuclar = [_dosyayi_tara(d) for d in dosyalar]
            return _sonucu_goster(sonuclar)

        elif islem == 'temizle':
            dosyalar = _skill_dosyalari(skill_adi)
            if not dosyalar:
                return "Temizlenecek dosya bulunamadi."

            temizlenen = 0
            for d in dosyalar:
                sonuc = _dosyayi_tara(d)
                if not sonuc["guvenli"]:
                    icerik = d.read_text(encoding="utf-8", errors="replace")
                    # Sadece raporla, otomatik temizleme yapma
                    temizlenen += 1

            return f"{temizlenen} dosyada guvenlik sorunu tespit edildi. El ile inceleme onerilir."

        elif islem == 'kontrol':
            if dosya_yolu:
                dosya = Path(dosya_yolu)
                if not dosya.exists():
                    return f"Dosya bulunamadi: {dosya_yolu}"
                sonuc = _dosyayi_tara(dosya)
                guvenli = sonuc["guvenli"]
                return f"{'GUVENLI' if guvenli else 'RISKLI'}: {dosya_yolu}"

            skill_adi = kwargs.get('skill_adi', '')
            dosyalar = _skill_dosyalari(skill_adi)
            if not dosyalar:
                return "Kontrol edilecek dosya bulunamadi."

            guvenli_sayisi = 0
            riskli_sayisi = 0
            for d in dosyalar:
                sonuc = _dosyayi_tara(d)
                if sonuc["guvenli"]:
                    guvenli_sayisi += 1
                else:
                    riskli_sayisi += 1

            return (
                f"Guvenlik kontrolu tamamlandi:\n"
                f"  Toplam dosya: {len(dosyalar)}\n"
                f"  Guvenli: {guvenli_sayisi}\n"
                f"  Riskli: {riskli_sayisi}"
            )

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Skill guvenlik hatasi: {e}"


def _sonucu_goster(sonuclar: list) -> str:
    """Tarama sonuclarini formatlar."""
    satirlar = ["=== Skill Guvenlik Taramasi ==="]
    toplam = len(sonuclar)
    guvenli = sum(1 for s in sonuclar if s["guvenli"])
    riskli = toplam - guvenli

    satirlar.append(f"Taranan dosya: {toplam}")
    satirlar.append(f"Guvenli: {guvenli}")
    satirlar.append(f"Riskli: {riskli}")

    for s in sonuclar:
        if not s["guvenli"]:
            satirlar.append(f"\nRISKLI: {s['dosya']}")
            if s["hassas_dosya_adi"]:
                satirlar.append(f"  Hassas dosya adi: {Path(s['dosya']).name}")
            if s["tehlikeli_kod"]:
                for k in set(s["tehlikeli_kod"]):
                    satirlar.append(f"  Tehlikeli kod: {k}")
            if s["api_anahtari"]:
                for k in set(s["api_anahtari"]):
                    satirlar.append(f"  API anahtari: {k[:12]}...")
            if s["sifre"]:
                for k in set(s["sifre"]):
                    satirlar.append(f"  Sifre/eslesme: {k[:20]}...")

    return "\n".join(satirlar)
