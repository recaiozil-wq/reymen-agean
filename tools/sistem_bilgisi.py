# -*- coding: utf-8 -*-
"""sistem_bilgisi.py — Sistem bilgisi aracı.

CPU, RAM, disk ve OS bilgilerini döndürür.
"""

import json
import os
import platform


def run(*args, **kwargs) -> str:
    """Sistem bilgilerini topla ve JSON olarak döndür."""
    try:
        bilgi = {
            "os": platform.system(),
            "os_versiyon": platform.version()[:80],
            "mimari": platform.machine(),
            "python": platform.python_version(),
            "cwd": os.getcwd(),
        }
        try:
            import psutil
            bilgi["cpu_sayi"] = psutil.cpu_count()
            bilgi["cpu_yuzde"] = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            bilgi["ram_toplam_gb"] = round(ram.total / 1024**3, 2)
            bilgi["ram_kullanim_yuzde"] = ram.percent
        except ImportError:
            bilgi["not"] = "psutil kurulu degil, detaylı CPU/RAM bilgisi yok"
        return json.dumps(bilgi, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print(run())
