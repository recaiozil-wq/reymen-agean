# -*- coding: utf-8 -*-
"""tools/sistem_bilgi.py — Sistem bilgisi toplama araci.

Disk kullanimi, bellek, calisan surecler ve diger sistem istatistikleri.
psutil kutuphanesini dener, yoksa shell komutlari ile fallback yapar.
"""

import logging
import platform
import subprocess
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def run(islem: str = "genel", **kwargs) -> dict:
    """Sistem bilgisi topla.

    Args:
        islem: "genel" (varsayilan), "disk", "bellek", "surec", "isletim_sistemi"

    Returns:
        dict: {"basarili": bool, "cikti": dict|str, "hata": str}
    """
    try:
        if islem == "genel":
            return _genel()
        elif islem == "disk":
            return _disk()
        elif islem == "bellek":
            return _bellek()
        elif islem == "surec":
            limit = kwargs.get("limit", 20)
            return _surecler(limit)
        elif islem == "isletim_sistemi":
            return _isletim_sistemi()
        else:
            return {
                "basarili": False, "cikti": "",
                "hata": f"Gecersiz islem: '{islem}'. Secenekler: genel, disk, bellek, surec, isletim_sistemi"
            }

    except Exception as e:
        logger.exception("Sistem bilgi hatasi")
        return {
            "basarili": False, "cikti": "",
            "hata": f"Beklenmeyen hata: {str(e)}"
        }


def _psutil_mevcut() -> bool:
    """psutil kutuphanesinin yuklu olup olmadigini kontrol et."""
    try:
        import psutil
        return True
    except ImportError:
        return False


def _genel() -> dict:
    """Genel sistem bilgisi (tum kategorileri birlestirir)."""
    try:
        import psutil
        return _genel_psutil()
    except ImportError:
        return _genel_shell()


def _genel_psutil() -> dict:
    """psutil ile genel sistem bilgisi."""
    import psutil

    cpu_count = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    # En cok CPU kullanan surecler
    procesos = []
    for p in sorted(psutil.process_iter(["pid", "name", "cpu_percent"]),
                     key=lambda x: x.info.get("cpu_percent", 0) or 0,
                     reverse=True)[:10]:
        try:
            procesos.append({
                "pid": p.info["pid"],
                "ad": p.info["name"],
                "cpu": p.info["cpu_percent"] or 0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    return {
        "basarili": True,
        "cikti": {
            "isletim_sistemi": platform.system(),
            "isletim_sistemi_detay": platform.platform(),
            "makine_adi": platform.node(),
            "cpu_sayisi": cpu_count,
            "cpu_kullanim": f"%{cpu_percent}",
            "bellek": {
                "toplam": _byte_insan(mem.total),
                "kullanilan": _byte_insan(mem.used),
                "bos": _byte_insan(mem.available),
                "kullanim_yuzde": f"%{mem.percent}"
            },
            "disk": {
                "toplam": _byte_insan(disk.total),
                "kullanilan": _byte_insan(disk.used),
                "bos": _byte_insan(disk.free),
                "kullanim_yuzde": f"%{disk.percent}"
            },
            "en_cok_cpu_harcayan_surecler": procesos
        },
        "hata": ""
    }


def _genel_shell() -> dict:
    """Shell komutlari ile genel sistem bilgisi (psutil yoksa)."""
    sonuc = {
        "isletim_sistemi": platform.system(),
        "isletim_sistemi_detay": platform.platform(),
        "makine_adi": platform.node(),
        "python_surumu": platform.python_version(),
    }

    # Disk bilgisi
    disk_bilgi, _ = _disk_shell()
    sonuc["disk"] = disk_bilgi

    # Bellek bilgisi
    bellek_bilgi, _ = _bellek_shell()
    sonuc["bellek"] = bellek_bilgi

    return {
        "basarili": True,
        "cikti": sonuc,
        "hata": "",
        "not": "psutil bulunamadi, shell komutlari kullanildi (sinirli bilgi)"
    }


def _disk() -> dict:
    """Disk kullanim bilgisi."""
    try:
        import psutil
        return _disk_psutil()
    except ImportError:
        return _disk_shell()[0]


def _disk_psutil() -> dict:
    """psutil ile disk bilgisi."""
    import psutil
    bolumler = {}
    for bolum in psutil.disk_partitions():
        try:
            kullanim = psutil.disk_usage(bolum.mountpoint)
            bolumler[bolum.mountpoint] = {
                "dosya_sistemi": bolum.fstype,
                "toplam": _byte_insan(kullanim.total),
                "kullanilan": _byte_insan(kullanim.used),
                "bos": _byte_insan(kullanim.free),
                "kullanim_yuzde": f"%{kullanim.percent}"
            }
        except (PermissionError, OSError):
            continue

    return {
        "basarili": True,
        "cikti": bolumler if bolumler else {"not": "Disk bilgisi alinamadi"},
        "hata": ""
    }


def _disk_shell() -> tuple:
    """Shell df komutu ile disk bilgisi."""
    try:
        if platform.system() == "Windows":
            # Windows: wmic veya powershell
            sonuc = subprocess.run(
                ["wmic", "logicaldisk", "get", "DeviceID,Size,FreeSpace",
                 "/format:csv"],
                capture_output=True, text=True, timeout=10
            )
            if sonuc.returncode != 0 or not sonuc.stdout.strip():
                return {}, "Disk bilgisi alinamadi"
            bolumler = {}
            satirlar = sonuc.stdout.strip().splitlines()
            for satir in satirlar[1:]:
                if not satir.strip():
                    continue
                parcalar = satir.split(",")
                if len(parcalar) >= 3:
                    harf = parcalar[1].strip()
                    try:
                        toplam = int(parcalar[2]) if parcalar[2] else 0
                        bos = int(parcalar[3]) if parcalar[3] else 0
                        kullanilan = toplam - bos
                        yuzde = round((kullanilan / toplam) * 100, 1) if toplam > 0 else 0
                        bolumler[harf] = {
                            "toplam": _byte_insan(toplam),
                            "kullanilan": _byte_insan(kullanilan),
                            "bos": _byte_insan(bos),
                            "kullanim_yuzde": f"%{yuzde}"
                        }
                    except (ValueError, TypeError):
                        continue
            return bolumler if bolumler else {}, ""
        else:
            # Linux/Mac: df -h
            sonuc = subprocess.run(
                ["df", "-h", "--type=ext4", "--type=xfs", "--type=btrfs",
                 "--type=ntfs", "--type=fat32"],
                capture_output=True, text=True, timeout=10
            )
            if sonuc.returncode != 0 or not sonuc.stdout.strip():
                sonuc = subprocess.run(
                    ["df", "-h"],
                    capture_output=True, text=True, timeout=10
                )
            return {"ham_cikti": sonuc.stdout.strip()}, ""
    except FileNotFoundError:
        return {}, "Disk komutu bulunamadi"
    except subprocess.TimeoutExpired:
        return {}, "Disk sorgusu zamani asildi"
    except Exception as e:
        return {}, f"Disk hatasi: {str(e)}"


def _bellek() -> dict:
    """Bellek kullanim bilgisi."""
    try:
        import psutil
        return _bellek_psutil()
    except ImportError:
        return _bellek_shell()[0]


def _bellek_psutil() -> dict:
    """psutil ile bellek bilgisi."""
    import psutil
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return {
        "basarili": True,
        "cikti": {
            "fiziksel_bellek": {
                "toplam": _byte_insan(mem.total),
                "kullanilan": _byte_insan(mem.used),
                "bos": _byte_insan(mem.available),
                "kullanim_yuzde": f"%{mem.percent}"
            },
            "swap": {
                "toplam": _byte_insan(swap.total),
                "kullanilan": _byte_insan(swap.used),
                "bos": _byte_insan(swap.free),
                "kullanim_yuzde": f"%{swap.percent}"
            }
        },
        "hata": ""
    }


def _bellek_shell() -> tuple:
    """Shell komutlari ile bellek bilgisi."""
    try:
        if platform.system() == "Windows":
            sonuc = subprocess.run(
                ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory",
                 "/format:csv"],
                capture_output=True, text=True, timeout=10
            )
            if sonuc.returncode == 0 and sonuc.stdout.strip():
                satirlar = sonuc.stdout.strip().splitlines()
                for satir in satirlar[1:]:
                    if not satir.strip():
                        continue
                    parcalar = satir.split(",")
                    if len(parcalar) >= 3:
                        try:
                            toplam_kb = int(parcalar[1])
                            bos_kb = int(parcalar[2])
                            kullanilan_kb = toplam_kb - bos_kb
                            yuzde = round((kullanilan_kb / toplam_kb) * 100, 1) if toplam_kb > 0 else 0
                            return {
                                "basarili": True,
                                "cikti": {
                                    "toplam": _byte_insan(toplam_kb * 1024),
                                    "kullanilan": _byte_insan(kullanilan_kb * 1024),
                                    "bos": _byte_insan(bos_kb * 1024),
                                    "kullanim_yuzde": f"%{yuzde}"
                                }
                            }, ""
                        except (ValueError, TypeError):
                            continue
            return {"basarili": False, "cikti": "", "hata": "Bellek bilgisi alinamadi"}, ""
        else:
            # Linux: free -h
            sonuc = subprocess.run(
                ["free", "-h"],
                capture_output=True, text=True, timeout=10
            )
            if sonuc.returncode == 0:
                return {
                    "basarili": True,
                    "cikti": {"ham_cikti": sonuc.stdout.strip()}
                }, ""
            return {"basarili": False, "cikti": "", "hata": "free komutu calismadi"}, ""
    except FileNotFoundError:
        return {"basarili": False, "cikti": "", "hata": "Bellek komutu bulunamadi"}, ""
    except Exception as e:
        return {"basarili": False, "cikti": "", "hata": f"Bellek hatasi: {str(e)}"}, ""


def _surecler(limit: int = 20) -> dict:
    """Calisan surecleri listele."""
    try:
        import psutil
        return _surecler_psutil(limit)
    except ImportError:
        return _surecler_shell(limit)


def _surecler_psutil(limit: int = 20) -> dict:
    """psutil ile surecleri listele."""
    import psutil
    surecler = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent",
                                   "status", "create_time"]):
        try:
            olusturma = datetime.fromtimestamp(
                p.info["create_time"]
            ).isoformat() if p.info["create_time"] else ""
            surecler.append({
                "pid": p.info["pid"],
                "ad": p.info["name"],
                "cpu": f"%{p.info['cpu_percent'] or 0}",
                "bellek": f"%{round(p.info['memory_percent'] or 0, 1)}",
                "durum": p.info["status"],
                "baslama": olusturma
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, TypeError):
            continue

    # CPU kullanimina gore sirala
    surecler.sort(key=lambda x: float(x["cpu"].replace("%", "") or 0), reverse=True)
    surecler = surecler[:limit]

    return {
        "basarili": True,
        "cikti": surecler,
        "hata": "",
        "toplam_surec": len(surecler),
        "limit": limit
    }


def _surecler_shell(limit: int = 20) -> dict:
    """Shell komutlari ile surecleri listele."""
    try:
        if platform.system() == "Windows":
            sonuc = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True, text=True, timeout=10
            )
            if sonuc.returncode == 0 and sonuc.stdout.strip():
                surecler = []
                satirlar = sonuc.stdout.strip().splitlines()[:limit]
                for satir in satirlar:
                    parcalar = satir.split(",")
                    if len(parcalar) >= 2:
                        ad = parcalar[0].strip('"')
                        pid = parcalar[1].strip('"')
                        surecler.append({"pid": pid, "ad": ad})
                return {
                    "basarili": True,
                    "cikti": surecler,
                    "hata": ""
                }
            return {"basarili": False, "cikti": "", "hata": "tasklist calismadi"}, ""
        else:
            # Linux: ps aux
            sonuc = subprocess.run(
                ["ps", "aux", "--sort=-%cpu"],
                capture_output=True, text=True, timeout=10
            )
            if sonuc.returncode == 0:
                satirlar = sonuc.stdout.strip().splitlines()
                baslik = satirlar[0] if satirlar else ""
                veri = satirlar[1:limit+1] if len(satirlar) > 1 else []
                return {
                    "basarili": True,
                    "cikti": {"baslik": baslik, "surecler": veri},
                    "hata": ""
                }
            return {"basarili": False, "cikti": "", "hata": "ps komutu calismadi"}, ""
    except FileNotFoundError:
        return {"basarili": False, "cikti": "", "hata": "Surec komutu bulunamadi"}, ""
    except Exception as e:
        return {"basarili": False, "cikti": "", "hata": f"Surec hatasi: {str(e)}"}, ""


def _isletim_sistemi() -> dict:
    """Isletim sistemi bilgisi."""
    import platform
    import sys
    return {
        "basarili": True,
        "cikti": {
            "sistem": platform.system(),
            "node": platform.node(),
            "surum": platform.version(),
            "makine": platform.machine(),
            "islemci": platform.processor(),
            "platform": platform.platform(),
            "python_surumu": sys.version
        },
        "hata": ""
    }


def _byte_insan(bayt: int) -> str:
    """Bayt degerini insan okunabilir formata cevir (KB, MB, GB, TB)."""
    if bayt is None:
        return "0 B"
    for birim in ["B", "KB", "MB", "GB", "TB"]:
        if abs(bayt) < 1024.0:
            return f"{bayt:.1f} {birim}"
        bayt /= 1024.0
    return f"{bayt:.1f} PB"


if __name__ == "__main__":
    import json
    print("=== SISTEM BILGISI (genel) ===")
    print(json.dumps(run(islem="genel"), ensure_ascii=False, indent=2))
