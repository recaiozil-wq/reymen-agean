#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
db_backup_wrapper.py â€” ReYMeN DB Yedekleme Wrapper

Kullanim: python db_backup_wrapper.py
          python db_backup_wrapper.py --full
          python db_backup_wrapper.py --check

Gorev:
  1. db_backup.py'yi alt surecte calistir
  2. Sonucu logla (dosya + stdout)
  3. Basarisizlikta findings_board'a kaydet
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
PROJE_KOK = Path(__file__).parent.parent.parent.parent
DB_BACKUP_PY = PROJE_KOK / "src" / "reymen" / "sistem" / "db_backup.py"
LOG_DOSYASI = PROJE_KOK / "logs" / "db_backup_wrapper.log"

os.makedirs(str(PROJE_KOK / "logs"), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(LOG_DOSYASI), encoding="utf-8"),
    ],
)
log = logging.getLogger("db_backup_wrapper")


# â”€â”€ Ana fonksiyon â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def calistir(ek_argumanlar: list = None) -> dict:
    """db_backup.py'yi calistir ve sonucu don."""
    if ek_argumanlar is None:
        ek_argumanlar = []

    log.info("DB yedekleme basliyor (args: %s)", " ".join(ek_argumanlar) if ek_argumanlar else "(gunluk)")
    baslangic = time.time()

    try:
        result = subprocess.run(
            [sys.executable, str(DB_BACKUP_PY)] + ek_argumanlar,
            capture_output=True, text=True, timeout=300,
            cwd=str(PROJE_KOK),
        )
        sure = round(time.time() - baslangic, 2)

        if result.returncode != 0:
            log.error("HATA kodu=%d stderr=%s", result.returncode, result.stderr[:500])
            return {"basarili": False, "hata": result.stderr[:1000]}

        cikti = {}
        try:
            cikti = json.loads(result.stdout)
        except json.JSONDecodeError:
            cikti = {"ham_cikti": result.stdout[:500]}

        cikti["sure_sn"] = sure
        basarili = cikti.get("basarili", 0)
        basarisiz = cikti.get("basarisiz", 0)
        log.info("Tamam: %d/%d basarili (%0.1f sn)", basarili, basarili + basarisiz, sure)
        return cikti

    except subprocess.TimeoutExpired:
        log.error("Zaman asimi (300 sn)")
        return {"basarili": False, "hata": "Zaman asimi"}
    except Exception as e:
        log.error("Beklenmeyen hata: %s", e)
        return {"basarili": False, "hata": str(e)}


if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    sonuc = calistir(args)
    print(json.dumps(sonuc, indent=2, ensure_ascii=False))

    # Basarisizlikta findings_board'a kaydet
    if not sonuc.get("basarili", True):
        try:
            sys.path.insert(0, str(PROJE_KOK))
            from reymen.sistem.findings_board import audit_tamamla
            audit_tamamla("kiral38", [{
                "konu": "db_backup_wrapper_basarisiz",
                "onem": "kritik",
                "aciklama": f"db_backup.py basarisiz: {sonuc.get('hata', 'bilinmiyor')}",
                "durum": "yeni",
            }])
            log.info("Bulgu panosuna kaydedildi")
        except Exception as e:
            log.warning("Bulgu panosu kayit hatasi: %s", e)
