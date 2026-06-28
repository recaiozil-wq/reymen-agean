# -*- coding: utf-8 -*-
"""disk_usage.py — Disk kullanımı sorgulama aracı.

Belirtilen dizin veya tüm disklerin kullanım bilgisini döndürür.
"""

import json
import os
from pathlib import Path

# Opsiyonel: psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


TOOL_META = {
    "aciklama": "Disk kullanım bilgisini sorgular (toplam, kullanılan, boş alan).",
    "parametreler": [
        {"ad": "dizin", "tip": "str", "aciklama": "Sorgulanacak dizin (varsayılan: mevcut dizin). 'tum' = tüm diskler."},
    ],
    "ornek": 'DISK_USAGE("C:/")',
    "kategori": "system",
}


def _format_bytes(b: int) -> str:
    """Bayt değerini insan okunabilir formata çevir."""
    for birim in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.2f} {birim}"
        b /= 1024
    return f"{b:.2f} PB"


def run(dizin: str = ".", *args, **kwargs) -> str:
    """Disk kullanımını sorgula.

    Args:
        dizin: Sorgulanacak dizin (varsayılan: '.'). 'tum' = tüm diskler/sürücüler.

    Returns:
        JSON: disk kullanım bilgileri.
    """
    try:
        if dizin.lower() in ("tum", "all", "tüm", "hepsi"):
            if HAS_PSUTIL:
                diskler = []
                for part in psutil.disk_partitions(all=False):
                    try:
                        usage = psutil.disk_usage(part.mountpoint)
                        diskler.append({
                            "surucu": part.device,
                            "mount": part.mountpoint,
                            "dosya_sistemi": part.fstype or "-",
                            "toplam": usage.total,
                            "toplam_str": _format_bytes(usage.total),
                            "kullanilan": usage.used,
                            "kullanilan_str": _format_bytes(usage.used),
                            "bos": usage.free,
                            "bos_str": _format_bytes(usage.free),
                            "kullanim_yuzde": usage.percent,
                        })
                    except (PermissionError, OSError):
                        continue
                return json.dumps({
                    "disk_sayisi": len(diskler),
                    "diskler": diskler,
                    "kaynak": "psutil",
                }, ensure_ascii=False, indent=2)
            else:
                # Windows: sürücü harflerini dene
                import string
                diskler = []
                for harf in string.ascii_uppercase:
                    surucu = f"{harf}:\\"
                    if os.path.exists(surucu):
                        try:
                            usage = os.statvfs(surucu) if hasattr(os, 'statvfs') else None
                            if usage:
                                toplam = usage.f_frsize * usage.f_blocks
                                bos = usage.f_frsize * usage.f_bfree
                                kullanilan = toplam - bos
                                diskler.append({
                                    "surucu": surucu,
                                    "toplam": toplam,
                                    "toplam_str": _format_bytes(toplam),
                                    "kullanilan": kullanilan,
                                    "kullanilan_str": _format_bytes(kullanilan),
                                    "bos": bos,
                                    "bos_str": _format_bytes(bos),
                                    "kullanim_yuzde": round(kullanilan / toplam * 100, 1) if toplam > 0 else 0,
                                })
                            else:
                                # statvfs yoksa sadece varlığını belirt
                                diskler.append({
                                    "surucu": surucu,
                                    "not": "Detayli bilgi icin psutil gerekli",
                                })
                        except Exception:
                            continue
                return json.dumps({
                    "disk_sayisi": len(diskler),
                    "diskler": diskler,
                    "kaynak": "os",
                    "not": "Detayli bilgi icin psutil kurun: pip install psutil",
                }, ensure_ascii=False, indent=2)

        # Tek dizin sorgula
        yol = Path(dizin).resolve()
        if not yol.exists():
            return json.dumps({"hata": f"Dizin bulunamadı: {dizin}"}, ensure_ascii=False)

        if HAS_PSUTIL:
            try:
                usage = psutil.disk_usage(str(yol))
                return json.dumps({
                    "dizin": str(yol),
                    "kaynak": "psutil",
                    "toplam": usage.total,
                    "toplam_str": _format_bytes(usage.total),
                    "kullanilan": usage.used,
                    "kullanilan_str": _format_bytes(usage.used),
                    "bos": usage.free,
                    "bos_str": _format_bytes(usage.free),
                    "kullanim_yuzde": usage.percent,
                }, ensure_ascii=False, indent=2)
            except (PermissionError, OSError) as e:
                return json.dumps({
                    "hata": f"Disk bilgisi alinamadi: {str(e)}",
                    "dizin": str(yol)
                }, ensure_ascii=False)
        else:
            try:
                st = yol.stat()
                return json.dumps({
                    "dizin": str(yol),
                    "kaynak": "os",
                    "not": "Detayli disk bilgisi icin psutil kurun: pip install psutil",
                    "dosya_boyutu": st.st_size,
                    "dosya_boyutu_str": _format_bytes(st.st_size),
                }, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps({
                    "hata": f"Dizin bilgisi alinamadi: {str(e)}"
                }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== MEVCUT DIZIN ===")
    print(run("."))
    print("\n=== TUM DISKLER ===")
    print(run("tum"))
