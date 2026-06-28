# -*- coding: utf-8 -*-
"""process_list.py — Çalışan process listesi aracı.

Sistemdeki çalışan process'leri listeler ve filtreler.
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
import subprocess


TOOL_META = {
    "aciklama": "Sistemdeki çalışan process'leri listeler ve isme göre filtreler.",
    "parametreler": [
        {"ad": "filtre", "tip": "str", "aciklama": "Process adına göre filtre (opsiyonel, boş = tümü)."},
        {"ad": "limit", "tip": "int", "aciklama": "Maksimum gösterilecek process sayısı (varsayılan: 50)."},
    ],
    "ornek": 'PROCESS_LIST(filtre="python", limit=10)',
    "kategori": "system",
}


def run(filtre: str = "", limit: int = 50, *args, **kwargs) -> str:
    """Çalışan process'leri listele.

    Args:
        filtre: Process adı filtresi (opsiyonel).
        limit: Maksimum gösterilecek process sayısı.

    Returns:
        JSON: process listesi.
    """
    try:
        if HAS_PSUTIL:
            processler = []
            for proc in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_percent", "create_time", "cmdline"]):
                try:
                    pinfo = proc.info
                    ad = pinfo.get("name") or ""
                    if filtre and filtre.lower() not in ad.lower():
                        continue
                    processler.append({
                        "pid": pinfo["pid"],
                        "ad": ad,
                        "durum": pinfo.get("status", ""),
                        "cpu": pinfo.get("cpu_percent"),
                        "memory": round(pinfo.get("memory_percent") or 0, 1),
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            processler.sort(key=lambda p: p.get("memory", 0), reverse=True)
            processler = processler[:limit]

            return json.dumps({
                "kaynak": "psutil",
                "filtre": filtre or "tumu",
                "toplam_bulunan": len(processler),
                "gosterilen": len(processler),
                "processler": processler,
            }, ensure_ascii=False, indent=2)

        else:
            # psutil yok: Windows tasklist veya Linux ps kullan
            try:
                if os.name == "nt":
                    cmd = ["tasklist", "/FO", "CSV", "/NH"]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    processler = []
                    for line in result.stdout.strip().split("\n"):
                        if not line.strip():
                            continue
                        parts = line.strip('"').split('","')
                        if len(parts) >= 2:
                            ad = parts[0]
                            pid = parts[1] if len(parts) > 1 else "?"
                            if not filtre or filtre.lower() in ad.lower():
                                processler.append({"ad": ad, "pid": pid})

                    processler = processler[:limit]
                    return json.dumps({
                        "kaynak": "tasklist",
                        "filtre": filtre or "tumu",
                        "toplam_bulunan": len(processler),
                        "processler": processler,
                        "not": "Detayli bilgi icin psutil kurun: pip install psutil",
                    }, ensure_ascii=False, indent=2)
                else:
                    cmd = ["ps", "aux"]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    processler = []
                    lines = result.stdout.strip().split("\n")
                    for line in lines[1:]:  # Header'ı atla
                        if not line.strip():
                            continue
                        parts = line.split()
                        if len(parts) >= 11:
                            ad = parts[10]
                            pid = parts[1]
                            if not filtre or filtre.lower() in ad.lower():
                                processler.append({"ad": ad, "pid": pid, "cpu": parts[2], "memory": parts[3]})

                    processler = processler[:limit]
                    return json.dumps({
                        "kaynak": "ps",
                        "filtre": filtre or "tumu",
                        "toplam_bulunan": len(processler),
                        "processler": processler,
                        "not": "Detayli bilgi icin psutil kurun: pip install psutil",
                    }, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps({
                    "hata": f"Process listesi alinamadi: {str(e)}",
                    "cozum": "pip install psutil",
                }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== PROCESS LIST (filtre yok) ===")
    print(run(limit=5))
