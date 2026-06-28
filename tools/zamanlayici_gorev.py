# -*- coding: utf-8 -*-
"""tools/zamanlayici_gorev.py — Cronjob sorgulama/ekleme/silme arayuzu.

crontab uzerinden zamanlanmis gorevleri yonetir.
"""

import logging
import subprocess
import shlex
from typing import Optional

logger = logging.getLogger(__name__)


def run(islem: str = "listele", cron_ifade: str = "", komut: str = "",
        hedef_satir: str = "", **kwargs) -> dict:
    """Cronjob'lari listele, ekle veya sil.

    Args:
        islem: "listele" (varsayilan), "ekle", "sil"
        cron_ifade: "ekle" islemi icin cron zamani (ornek: "0 5 * * *")
        komut: "ekle" islemi icin calistirilacak komut
        hedef_satir: "sil" islemi icin silinecek satir (kismi eslesme)

    Returns:
        dict: {"basarili": bool, "cikti": str, "hata": str}
    """
    try:
        import shlex
    except ImportError:
        logger.warning("[fix_01_sessiz_except] ImportError")

    try:
        if islem == "listele":
            return _listele()
        elif islem == "ekle":
            return _ekle(cron_ifade, komut)
        elif islem == "sil":
            return _sil(hedef_satir)
        else:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Gecersiz islem: '{islem}'. Secenekler: listele, ekle, sil"
            }
    except Exception as e:
        logger.exception("Zamanlayici_gorev hatasi")
        return {
            "basarili": False,
            "cikti": "",
            "hata": f"Beklenmeyen hata: {str(e)}"
        }


def _listele() -> dict:
    """Mevcut cronjob'lari listele."""
    try:
        sonuc = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=15
        )
        if sonuc.returncode == 0 and sonuc.stdout.strip():
            satirlar = sonuc.stdout.strip().splitlines()
            return {
                "basarili": True,
                "cikti": "\n".join(satirlar) if satirlar else "(hic cronjob yok)",
                "hata": ""
            }
        else:
            # crontab -l bos dondu veya hata verdi
            hata = sonuc.stderr.strip()
            if "no crontab" in hata.lower() or not hata:
                return {
                    "basarili": True,
                    "cikti": "(hic cronjob yok)",
                    "hata": ""
                }
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Crontab okunamadi: {hata or 'bilinmeyen hata'}"
            }
    except FileNotFoundError:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "crontab komutu bulunamadi. Bu sistemde cron kurulu olmayabilir."
        }
    except subprocess.TimeoutExpired:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "Crontab okuma zamani asildi."
        }
    except Exception as e:
        logger.exception("Cron listeleme hatasi")
        return {
            "basarili": False,
            "cikti": "",
            "hata": f"Cron listeleme hatasi: {str(e)}"
        }


def _ekle(cron_ifade: str, komut: str) -> dict:
    """Yeni cronjob ekle."""
    if not cron_ifade or not komut:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "cron_ifade ve komut parametreleri zorunludur."
        }

    # Cron ifade dogrulama (5 alanli basit kontrol)
    if not _cron_ifade_dogrula(cron_ifade):
        return {
            "basarili": False,
            "cikti": "",
            "hata": (f"Gecersiz cron ifadesi: '{cron_ifade}'. "
                     f"Ornek: '0 5 * * *' (5 alanli olmali)")
        }

    try:
        # Mevcut cronjob'lari al
        mevcut = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=15
        )
        mevcut_satirlar = mevcut.stdout.strip().splitlines() if mevcut.returncode == 0 and mevcut.stdout.strip() else []

        yeni_satir = f"{cron_ifade} {komut}"

        # Ayni satir varsa ekleme
        if yeni_satir in mevcut_satirlar:
            return {
                "basarili": True,
                "cikti": f"Bu cronjob zaten mevcut: {yeni_satir}",
                "hata": ""
            }

        mevcut_satirlar.append(yeni_satir)
        yeni_icerik = "\n".join(mevcut_satirlar) + "\n"

        sonuc = subprocess.run(
            ["crontab", "-"],
            input=yeni_icerik, capture_output=True, text=True, timeout=15
        )
        if sonuc.returncode == 0:
            return {
                "basarili": True,
                "cikti": f"Cronjob eklendi: {yeni_satir}",
                "hata": ""
            }
        else:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Cronjob eklenemedi: {sonuc.stderr.strip()}"
            }
    except FileNotFoundError:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "crontab komutu bulunamadi. Bu sistemde cron kurulu olmayabilir."
        }
    except subprocess.TimeoutExpired:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "Cron islemi zamani asildi."
        }
    except Exception as e:
        logger.exception("Cron ekleme hatasi")
        return {
            "basarili": False,
            "cikti": "",
            "hata": f"Cron ekleme hatasi: {str(e)}"
        }


def _sil(hedef_satir: str) -> dict:
    """Cronjob sil (satir icinde eslesme ile)."""
    if not hedef_satir:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "hedef_satir parametresi zorunludur."
        }

    try:
        mevcut = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True, timeout=15
        )
        if mevcut.returncode != 0 or not mevcut.stdout.strip():
            return {
                "basarili": False,
                "cikti": "",
                "hata": "Crontab bos veya okunamadi."
            }

        satirlar = mevcut.stdout.strip().splitlines()
        eslesen = [s for s in satirlar if hedef_satir in s]

        if not eslesen:
            return {
                "basarili": True,
                "cikti": f"Eslesen cronjob bulunamadi: '{hedef_satir}'",
                "hata": ""
            }

        kalan = [s for s in satirlar if hedef_satir not in s]
        yeni_icerik = "\n".join(kalan) + "\n" if kalan else ""

        sonuc = subprocess.run(
            ["crontab", "-"],
            input=yeni_icerik, capture_output=True, text=True, timeout=15
        )
        if sonuc.returncode == 0:
            return {
                "basarili": True,
                "cikti": f"{len(eslesen)} cronjob silindi:\n" + "\n".join(eslesen),
                "hata": ""
            }
        else:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Cronjob silinemedi: {sonuc.stderr.strip()}"
            }
    except FileNotFoundError:
        return {
            "basarili": False,
            "cikti": "",
            "hata": "crontab komutu bulunamadi."
        }
    except Exception as e:
        logger.exception("Cron silme hatasi")
        return {
            "basarili": False,
            "cikti": "",
            "hata": f"Cron silme hatasi: {str(e)}"
        }


def _cron_ifade_dogrula(ifade: str) -> bool:
    """Cron ifadesinin 5 alanli olup olmadigini dogrula."""
    parcalar = ifade.strip().split()
    if len(parcalar) != 5:
        return False
    gecerli_karakterler = set("0123456789*,-/")
    for p in parcalar:
        for c in p:
            if c not in gecerli_karakterler:
                return False
    return True


if __name__ == "__main__":
    print("=== CRON LISTELE ===")
    print(run(islem="listele"))
