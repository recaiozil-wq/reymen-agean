# -*- coding: utf-8 -*-
"""skills_sync.py — Skill Senkronizasyonu.

GitHub Watcher-Hermes/ReYMeN-skills reposundan skill çeker (indir) veya
lokal skill'leri GitHub'a yollar (yukle). gh CLI kullanır.
gh CLI mevcut değilse otomatik kurulum yapmaz, hata döndürür.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional
import logging
logger = logging.getLogger(__name__)

# Varsayılan ayarlar
PROJE_KOKU = Path(__file__).parent.parent.resolve()
SKILLS_KLASOR = PROJE_KOKU / ".ReYMeN" / "skills"
GITHUB_REPO = "Watcher-Hermes/ReYMeN-skills"

# gh CLI yolları (öncelik sırasına göre)
GH_CLI_YOLLARI = [
    "gh",  # PATH'te varsa (Linux/macOS/Windows)
    "C:\\Program Files\\GitHub CLI\\gh.exe",
    "C:\\Program Files (x86)\\GitHub CLI\\gh.exe",
]


def _gh_bul() -> Optional[str]:
    """Sistemde gh CLI'in yolunu bul. Bulamazsa None döndür."""
    for yol in GH_CLI_YOLLARI:
        try:
            sonuc = subprocess.run(
                [yol, "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                shell=(yol == "gh"),  # PATH'teki gh için shell gerekebilir
            )
            if sonuc.returncode == 0:
                return yol
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    return None


def _gh_komut(gh_yol: str, args: list[str]) -> dict:
    """gh CLI komutunu çalıştır, sonucu dict olarak döndür."""
    try:
        sonuc = subprocess.run(
            [gh_yol] + args,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "basarili": sonuc.returncode == 0,
            "cikti": sonuc.stdout.strip(),
            "hata": sonuc.stderr.strip(),
            "kod": sonuc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"basarili": False, "cikti": "", "hata": "Zaman aşımı (60sn)", "kod": -1}
    except Exception as e:
        return {"basarili": False, "cikti": "", "hata": str(e), "kod": -1}


def _indir(dal: str) -> dict:
    """GitHub reposundan skill'leri indir (gh repo clone + kopyala)."""
    gh_yol = _gh_bul()
    if not gh_yol:
        return {
            "basarili": False,
            "hata": "gh CLI bulunamadı. Lütfen GitHub CLI'ı yükleyin: https://cli.github.com/",
        }

    # Geçici dizin oluştur
    import tempfile
    gecici_klasor = Path(tempfile.mkdtemp(prefix="ReYMeN_skills_"))
    hedef_klasor = gecici_klasor / "ReYMeN-skills"

    try:
        # Clone
        komut_sonuc = _gh_komut(gh_yol, [
            "repo", "clone", GITHUB_REPO,
            str(hedef_klasor),
            "--", "--branch", dal,
        ])
        if not komut_sonuc["basarili"]:
            return {
                "basarili": False,
                "hata": f"Repo klonlanamadı: {komut_sonuc['hata']}",
                "detay": komut_sonuc,
            }

        # Skills klasörünü hazırla
        SKILLS_KLASOR.mkdir(parents=True, exist_ok=True)
        kaynak_skills = hedef_klasor / "skills"

        if not kaynak_skills.exists():
            return {
                "basarili": False,
                "hata": f"Repoda 'skills/' klasörü bulunamadı. {kaynak_skills}",
            }

        # Kategorileri kopyala
        import shutil
        kopyalanan = 0
        for kategori in kaynak_skills.iterdir():
            if not kategori.is_dir():
                continue
            hedef_kategori = SKILLS_KLASOR / kategori.name
            hedef_kategori.mkdir(parents=True, exist_ok=True)
            for skill_dizini in kategori.iterdir():
                if not skill_dizini.is_dir():
                    continue
                hedef_skill = hedef_kategori / skill_dizini.name
                if hedef_skill.exists():
                    shutil.rmtree(hedef_skill)
                shutil.copytree(skill_dizini, hedef_skill)
                kopyalanan += 1

        return {
            "basarili": True,
            "mesaj": f"{kopyalanan} skill başarıyla indirildi (dal: {dal}).",
            "kaynak": GITHUB_REPO,
            "dal": dal,
            "skill_sayisi": kopyalanan,
        }
    except Exception as e:
        return {"basarili": False, "hata": f"İndirme hatası: {e}"}
    finally:
        # Temizlik
        try:
            import shutil
            shutil.rmtree(gecici_klasor, ignore_errors=True)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")


def _yukle(dal: str) -> dict:
    """Lokal skill'leri GitHub reposuna yükle (gh CLI ile PR oluştur)."""
    gh_yol = _gh_bul()
    if not gh_yol:
        return {
            "basarili": False,
            "hata": "gh CLI bulunamadı. Lütfen GitHub CLI'ı yükleyin: https://cli.github.com/",
        }

    if not SKILLS_KLASOR.exists():
        return {
            "basarili": False,
            "hata": f"Lokal skills klasörü bulunamadı: {SKILLS_KLASOR}",
        }

    import tempfile
    import shutil
    gecici_klasor = Path(tempfile.mkdtemp(prefix="ReYMeN_skills_"))
    repo_klasor = gecici_klasor / "ReYMeN-skills"

    try:
        # Repoyu clone (gh ile fork + clone)
        komut_sonuc = _gh_komut(gh_yol, [
            "repo", "fork", GITHUB_REPO,
            "--clone", "--", "--branch", dal,
        ])
        # Alternatif: doğrudan clone dene
        if not komut_sonuc["basarili"]:
            # Doğrudan clone dene (fork yoksa hata verir)
            komut_sonuc = _gh_komut(gh_yol, [
                "repo", "clone", GITHUB_REPO,
                str(repo_klasor),
                "--", "--branch", dal,
            ])
            if not komut_sonuc["basarili"]:
                return {
                    "basarili": False,
                    "hata": f"Repo klonlanamadı: {komut_sonuc['hata']}",
                }

        # Lokal skill'leri repo içine kopyala
        hedef_skills = repo_klasor / "skills"
        hedef_skills.mkdir(parents=True, exist_ok=True)

        kopyalanan = 0
        for kategori in SKILLS_KLASOR.iterdir():
            if not kategori.is_dir():
                continue
            hedef_kategori = hedef_skills / kategori.name
            hedef_kategori.mkdir(parents=True, exist_ok=True)
            for skill_dizini in kategori.iterdir():
                if not skill_dizini.is_dir():
                    continue
                hedef_skill = hedef_kategori / skill_dizini.name
                if hedef_skill.exists():
                    shutil.rmtree(hedef_skill)
                shutil.copytree(skill_dizini, hedef_skill)
                kopyalanan += 1

        # Git commit + push + PR
        import datetime
        zaman = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Git işlemleri
        for cmd, args_list in [
            ("add", ["-A"]),
            ("commit", ["-m", f"Skill güncellemesi: {kopyalanan} skill senkronize edildi ({zaman})"]),
            ("push", ["origin", dal]),
        ]:
            sonuc = subprocess.run(
                ["git", cmd] + args_list,
                capture_output=True, text=True, timeout=30,
                cwd=str(repo_klasor),
            )
            if sonuc.returncode != 0 and cmd != "add":
                # Commit başarısızsa (değişiklik yok) devam et
                if "nothing to commit" in sonuc.stderr:
                    break
                return {
                    "basarili": False,
                    "hata": f"git {cmd} hatası: {sonuc.stderr.strip()}",
                }

        # PR oluştur (gh CLI ile)
        pr_sonuc = _gh_komut(gh_yol, [
            "pr", "create",
            "--repo", GITHUB_REPO,
            "--base", dal,
            "--head", f"$(whoami):{dal}",
            "--title", f"Skill Senkronizasyonu ({zaman})",
            "--body", f"{kopyalanan} adet skill ReYMeN projesinden senkronize edildi.\n\nOtomatik oluşturuldu: {zaman}",
        ])

        return {
            "basarili": True,
            "mesaj": f"{kopyalanan} skill başarıyla yüklendi.",
            "dal": dal,
            "skill_sayisi": kopyalanan,
            "pr_durumu": pr_sonuc,
        }
    except Exception as e:
        return {"basarili": False, "hata": f"Yükleme hatası: {e}"}
    finally:
        try:
            shutil.rmtree(gecici_klasor, ignore_errors=True)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")


def run(**kwargs) -> str:
    """Ana giriş noktası — skill senkronizasyonu.

    Args:
        yon: "indir" (GitHub'dan çek) veya "yukle" (GitHub'a gönder)
        dal: GitHub branch adı (varsayılan: "main")

    Returns:
        JSON string
    """
    try:
        yon = kwargs.get("yon", "indir")
        dal = kwargs.get("dal", "main")

        if yon not in ("indir", "yukle"):
            return json.dumps({
                "basarili": False,
                "hata": f"Geçersiz yön: '{yon}'. 'indir' veya 'yukle' olmalı.",
            }, ensure_ascii=False)

        if yon == "indir":
            sonuc = _indir(dal)
        else:
            sonuc = _yukle(dal)

        return json.dumps(sonuc, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "basarili": False,
            "hata": f"Beklenmeyen hata: {e}",
        }, ensure_ascii=False)


if __name__ == "__main__":
    print("=== İndirme Testi ===")
    print(run(yon="indir", dal="main"))
