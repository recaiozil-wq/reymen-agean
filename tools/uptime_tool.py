# -*- coding: utf-8 -*-
"""uptime_tool.py — Sistem çalışma süresi sorgulama aracı.

Sistemin ne kadar süredir çalıştığını döndürür.
"""

import json
import os
import time
import platform
import logging
logger = logging.getLogger(__name__)

# Opsiyonel: psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Opsiyonel: subprocess (Linux /proc/uptime için)
import subprocess


TOOL_META = {
    "aciklama": "Sistemin ne kadar süredir çalıştığını döndürür.",
    "parametreler": [
        {"ad": "format", "tip": "str", "aciklama": "'insan' (varsayılan) veya 'saniye' çıktı formatı."},
    ],
    "ornek": 'UPTIME_TOOL(format="insan")',
    "kategori": "system",
}


def _saniyeyi_formatla(saniye: float) -> str:
    """Saniye değerini insan okunabilir formata çevir."""
    gun = int(saniye // 86400)
    saat = int((saniye % 86400) // 3600)
    dakika = int((saniye % 3600) // 60)
    sn = int(saniye % 60)

    parcalar = []
    if gun > 0:
        parcalar.append(f"{gun} gun")
    if saat > 0:
        parcalar.append(f"{saat} saat")
    if dakika > 0:
        parcalar.append(f"{dakika} dakika")
    if sn > 0 or not parcalar:
        parcalar.append(f"{sn} saniye")

    return ", ".join(parcalar)


def run(sonuc_format: str = "insan", *args, **kwargs) -> str:
    """Sistem çalışma süresini sorgula.

    Args:
        sonuc_format: 'insan' (varsayılan) veya 'saniye'.

    Returns:
        JSON: uptime bilgisi.
    """
    try:
        uptime_saniye = None

        if HAS_PSUTIL:
            # psutil ile (çapraz platform)
            boot_time = psutil.boot_time()
            uptime_saniye = time.time() - boot_time
            kaynak = "psutil"
        elif platform.system() == "Linux":
            # /proc/uptime
            try:
                with open("/proc/uptime", "r") as f:
                    uptime_saniye = float(f.read().split()[0])
                kaynak = "/proc/uptime"
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
        elif platform.system() == "Windows":
            # Windows: WMI veya uptime hesaplama
            try:
                result = subprocess.run(
                    ["wmic", "os", "get", "lastbootuptime"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    # Basit uptime: sistem başlangıcından beri geçen süre
                    # Alternatif: net stats workstation
                    result2 = subprocess.run(
                        ["net", "stats", "workstation"],
                        capture_output=True, text=True, timeout=5
                    )
                    for line in result2.stdout.split("\n"):
                        if "Istatistik" in line or "since" in line.lower():
                            kaynak = "net_stats"
                            break
                    # Fallback: boot time'dan hesapla
                    import ctypes
                    lib = ctypes.windll.kernel32
                    tick_count = lib.GetTickCount64()
                    uptime_saniye = tick_count / 1000.0
                    kaynak = "GetTickCount64"
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        if uptime_saniye is None:
            return json.dumps({
                "hata": "Uptime bilgisi alinamadi. psutil yardimiyla alinabilir: pip install psutil"
            }, ensure_ascii=False)

        if sonuc_format == "saniye":
            return json.dumps({
                "uptime_saniye": round(uptime_saniye, 2),
                "kaynak": kaynak,
            }, ensure_ascii=False, indent=2)
        else:
            return json.dumps({
                "uptime": _saniyeyi_formatla(uptime_saniye),
                "uptime_saniye": round(uptime_saniye, 2),
                "kaynak": kaynak,
            }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== UPTIME ===")
    print(run(sonuc_format="insan"))
    print("\n=== UPTIME (saniye) ===")
    print(run(sonuc_format="saniye"))
