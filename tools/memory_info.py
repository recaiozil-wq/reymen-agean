# -*- coding: utf-8 -*-
"""memory_info.py — RAM kullanım bilgisi aracı.

Sistemdeki RAM (bellek) kullanım bilgilerini döndürür.
"""

import json

# Opsiyonel: psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Opsiyonel: os (built-in, sınırlı)
import os


TOOL_META = {
    "aciklama": "Sistem RAM (bellek) kullanım bilgisini döndürür: toplam, kullanılan, boş RAM.",
    "parametreler": [
        {"ad": "detayli", "tip": "bool", "aciklama": "Detaylı bellek bilgisi (swap dahil) gösterilsin mi? (varsayılan: false)."},
    ],
    "ornek": 'MEMORY_INFO(detayli=true)',
    "kategori": "system",
}


def _format_bytes(b: int) -> str:
    """Bayt değerini insan okunabilir formata çevir."""
    for birim in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.2f} {birim}"
        b /= 1024
    return f"{b:.2f} PB"


def run(detayli: bool = False, *args, **kwargs) -> str:
    """RAM kullanım bilgisini sorgula.

    Args:
        detayli: Detaylı bellek bilgisi (swap, buffers, cached) gösterilsin mi?

    Returns:
        JSON: bellek kullanım bilgileri.
    """
    try:
        if HAS_PSUTIL:
            mem = psutil.virtual_memory()
            sonuc = {
                "kaynak": "psutil",
                "toplam": mem.total,
                "toplam_str": _format_bytes(mem.total),
                "kullanilan": mem.used,
                "kullanilan_str": _format_bytes(mem.used),
                "bos": mem.available,
                "bos_str": _format_bytes(mem.available),
                "kullanim_yuzde": mem.percent,
            }

            if detayli:
                sonuc.update({
                    "aktif": mem.active,
                    "aktif_str": _format_bytes(mem.active),
                    "pasif": getattr(mem, "inactive", 0),
                    "pasif_str": _format_bytes(getattr(mem, "inactive", 0)),
                    "buffer": getattr(mem, "buffers", 0),
                    "buffer_str": _format_bytes(getattr(mem, "buffers", 0)),
                    "cache": getattr(mem, "cached", 0),
                    "cache_str": _format_bytes(getattr(mem, "cached", 0)),
                })

                # Swap bilgisi
                try:
                    swap = psutil.swap_memory()
                    sonuc["swap"] = {
                        "toplam": swap.total,
                        "toplam_str": _format_bytes(swap.total),
                        "kullanilan": swap.used,
                        "kullanilan_str": _format_bytes(swap.used),
                        "bos": swap.free,
                        "bos_str": _format_bytes(swap.free),
                        "kullanim_yuzde": swap.percent,
                    }
                except Exception:
                    sonuc["swap"] = {"hata": "Swap bilgisi alinamadi"}

            return json.dumps(sonuc, ensure_ascii=False, indent=2)

        else:
            # Linux: /proc/meminfo
            if os.path.exists("/proc/meminfo"):
                try:
                    meminfo = {}
                    with open("/proc/meminfo", "r") as f:
                        for line in f:
                            if ":" in line:
                                key, val = line.split(":", 1)
                                meminfo[key.strip()] = val.strip()

                    toplam_kb = int(meminfo.get("MemTotal", "0 kB").split()[0])
                    bos_kb = int(meminfo.get("MemAvailable", "0 kB").split()[0])
                    kullanilan_kb = toplam_kb - bos_kb

                    return json.dumps({
                        "kaynak": "/proc/meminfo",
                        "toplam": toplam_kb * 1024,
                        "toplam_str": _format_bytes(toplam_kb * 1024),
                        "kullanilan": kullanilan_kb * 1024,
                        "kullanilan_str": _format_bytes(kullanilan_kb * 1024),
                        "bos": bos_kb * 1024,
                        "bos_str": _format_bytes(bos_kb * 1024),
                        "kullanim_yuzde": round(kullanilan_kb / toplam_kb * 100, 1) if toplam_kb > 0 else 0,
                        "not": "Detayli bilgi icin psutil kurun: pip install psutil",
                    }, ensure_ascii=False, indent=2)
                except Exception as e:
                    return json.dumps({"hata": f"/proc/meminfo okuma hatasi: {str(e)}"}, ensure_ascii=False)

            # Windows: kernel32.GlobalMemoryStatusEx
            try:
                import ctypes
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong),
                        ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong),
                        ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong),
                        ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                    ]

                mem_status = MEMORYSTATUSEX()
                mem_status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(mem_status))

                return json.dumps({
                    "kaynak": "kernel32",
                    "toplam": mem_status.ullTotalPhys,
                    "toplam_str": _format_bytes(mem_status.ullTotalPhys),
                    "kullanilan": mem_status.ullTotalPhys - mem_status.ullAvailPhys,
                    "kullanilan_str": _format_bytes(mem_status.ullTotalPhys - mem_status.ullAvailPhys),
                    "bos": mem_status.ullAvailPhys,
                    "bos_str": _format_bytes(mem_status.ullAvailPhys),
                    "kullanim_yuzde": mem_status.dwMemoryLoad,
                    "not": "Detayli bilgi icin psutil kurun: pip install psutil",
                }, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps({
                    "hata": f"Bellek bilgisi alinamadi: {str(e)}",
                    "cozum": "pip install psutil",
                }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== RAM BILGISI ===")
    print(run(detayli=True))
