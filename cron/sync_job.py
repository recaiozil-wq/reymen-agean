"""
cron/sync_job.py — Senkronizasyon cron job'u.

GitHub yedekleme, skill senkronizasyonu.
ReYMeN veri senkronizasyon altyapısı için görev.
"""

import logging
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


def _git_komut(calisma_dizini, *args):
    """Git komutunu çalıştırır, (basari, cikti) döndürür."""
    try:
        sonuc = subprocess.run(
            ["git"] + list(args),
            capture_output=True,
            text=True,
            timeout=60,
            cwd=calisma_dizini,
        )
        if sonuc.returncode == 0:
            return True, sonuc.stdout.strip()
        else:
            return False, sonuc.stderr.strip()
    except FileNotFoundError:
        return False, "git komutu bulunamadı"
    except subprocess.TimeoutExpired:
        return False, "zaman aşımı"
    except Exception as e:
        return False, str(e)


def _github_yedekle(proje_kok):
    """GitHub'a otomatik commit ve push yapar."""
    durum = {}

    try:
        # Git reposu mu kontrol et
        basari, _ = _git_komut(str(proje_kok), "rev-parse", "--git-dir")
        if not basari:
            durum["git_repo"] = "bulunamadi"
            logger.warning("Git repo bulunamadı")
            return durum

        durum["git_repo"] = "mevcut"

        # Değişiklikleri kontrol et
        basari, cikti = _git_komut(str(proje_kok), "status", "--porcelain")
        if not basari:
            durum["durum_kontrol"] = "hata"
            return durum

        if not cikti.strip():
            durum["degisiklik"] = "yok"
            logger.info("📡 GitHub: Değişiklik yok, yedekleme gerekmiyor")
            return durum

        durum["degisiklik"] = "var"

        # Stage all
        basari, cikti = _git_komut(str(proje_kok), "add", "-A")
        if not basari:
            durum["stage"] = "hata"
            durum["stage_hata"] = cikti
            logger.error("Git stage hatası: %s", cikti)
            return durum
        durum["stage"] = "basarili"

        # Commit
        zaman = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_msg = f"🔄 ReYMeN otomatik yedekleme - {zaman}"
        basari, cikti = _git_komut(str(proje_kok), "commit", "-m", commit_msg)
        if not basari:
            durum["commit"] = "hata"
            durum["commit_hata"] = cikti
            logger.error("Git commit hatası: %s", cikti)
            return durum
        durum["commit"] = "basarili"

        # Push
        basari, cikti = _git_komut(str(proje_kok), "push")
        if not basari:
            durum["push"] = "hata"
            durum["push_hata"] = cikti
            logger.warning("Git push hatası: %s (repo erişilebilir olmayabilir)", cikti)
            return durum

        durum["push"] = "basarili"
        logger.info("📡 GitHub yedekleme başarılı: %s", commit_msg)
        return durum

    except Exception as e:
        logger.error("GitHub yedekleme hatası: %s", e)
        durum["genel_hata"] = str(e)
        return durum


def _skill_senkronizasyonu(proje_kok):
    """Skills klasörünü senkronize eder."""
    durum = {}

    try:
        skills_kaynak = proje_kok / "skills"
        if not skills_kaynak.exists():
            durum["skills_klasoru"] = "bulunamadi"
            logger.debug("Skills klasörü bulunamadı: %s", skills_kaynak)
            return durum

        durum["skills_klasoru"] = "mevcut"
        skill_listesi = []
        for item in skills_kaynak.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                skill_listesi.append(item.name)

        durum["skill_sayisi"] = len(skill_listesi)
        durum["skill_listesi"] = skill_listesi
        logger.info("📡 Skills senkronizasyonu: %d skill bulundu", len(skill_listesi))

        # Skill metadata kontrolü
        saglikli = 0
        hatali = 0
        for skill_adi in skill_listesi:
            skill_path = skills_kaynak / skill_adi
            init_file = skill_path / "__init__.py"
            if init_file.exists():
                saglikli += 1
            else:
                hatali += 1
                logger.warning("Skill __init__.py eksik: %s", skill_adi)

        durum["saglikli_skill"] = saglikli
        durum["hatali_skill"] = hatali

        return durum

    except Exception as e:
        logger.error("Skill senkronizasyon hatası: %s", e)
        durum["genel_hata"] = str(e)
        return durum


def calistir():
    """Senkronizasyon job'unun ana çalıştırma fonksiyonu."""
    try:
        proje_kok = Path(__file__).resolve().parent.parent
        sonuc = {
            "tarih": datetime.now().isoformat(),
            "proje": str(proje_kok),
        }

        # 1. GitHub yedekleme
        try:
            github_durum = _github_yedekle(proje_kok)
            sonuc["github"] = github_durum
        except Exception as e:
            sonuc["github"] = {"hata": str(e)}
            logger.error("GitHub yedekleme hatası: %s", e)

        # 2. Skill senkronizasyonu
        try:
            skill_durum = _skill_senkronizasyonu(proje_kok)
            sonuc["skills"] = skill_durum
        except Exception as e:
            sonuc["skills"] = {"hata": str(e)}
            logger.error("Skill senkronizasyon hatası: %s", e)

        logger.info("📡 Senkronizasyon tamamlandı: GitHub=%s, Skills=%s",
                    sonuc.get("github", {}).get("durum", "?"),
                    sonuc.get("skills", {}).get("skill_sayisi", "?"))

        return sonuc

    except Exception as e:
        logger.error("❌ Senkronizasyon job'ı başarısız: %s", e)
        return {"hata": str(e)}


def bilgi():
    """Job metadata döndürür."""
    return {
        "isim": "senkronizasyon",
        "interval": "saatte 1 kez",
        "aciklama": "GitHub yedekleme ve skill senkronizasyonu",
        "versiyon": "1.0.0",
    }
