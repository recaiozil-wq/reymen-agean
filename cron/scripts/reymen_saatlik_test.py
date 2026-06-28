# -*- coding: utf-8 -*-
"""cron/scripts/reymen_saatlik_test.py — ReYMeN Saatlik Test Kosucusu.

test_suite.py ve test_providers.py'yi calistirir, sonuclari kaydeder.
Venv Python'ini otomatik bulur, eksik ortam sorununu onler.

Calistir:
    python cron/scripts/reymen_saatlik_test.py
    python cron/scripts/reymen_saatlik_test.py --verbose
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.resolve()
LOG_DIR = Path.home() / ".ReYMeN" / "cron" / "output" / "reymen-saatlik-test"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def _venv_python() -> str:
    """Projeye ait venv Python yorumlayicisini bulur; yoksa sistem Python'ini doner."""
    candidates = [
        ROOT / "venv" / "Scripts" / "python.exe",  # Windows
        ROOT / "venv" / "bin" / "python",           # Unix
        ROOT / ".venv" / "Scripts" / "python.exe",
        ROOT / ".venv" / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return sys.executable


def _calistir(python: str, betik: str, ek_args: list = None) -> dict:
    """Bir Python betigini subprocess ile calistirir, sonucu toplar."""
    cmd = [python, betik] + (ek_args or [])
    baslangic = datetime.now()
    try:
        sonuc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
        )
        bitis = datetime.now()
        return {
            "betik": betik,
            "cikis_kodu": sonuc.returncode,
            "stdout": sonuc.stdout,
            "stderr": sonuc.stderr[-2000:] if sonuc.stderr else "",
            "sure_sn": round((bitis - baslangic).total_seconds(), 2),
            "basarili": sonuc.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "betik": betik,
            "cikis_kodu": -1,
            "stdout": "",
            "stderr": "TIMEOUT: 300 saniye asild",
            "sure_sn": 300,
            "basarili": False,
        }
    except Exception as e:
        return {
            "betik": betik,
            "cikis_kodu": -1,
            "stdout": "",
            "stderr": str(e),
            "sure_sn": 0,
            "basarili": False,
        }


def _pytest_calistir(python: str, hedef: str) -> dict:
    """pytest ile bir test dosyasini/klasorunu calistirir."""
    cmd = [python, "-m", "pytest", hedef, "--tb=short", "-q"]
    baslangic = datetime.now()
    try:
        sonuc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        bitis = datetime.now()
        return {
            "hedef": hedef,
            "cikis_kodu": sonuc.returncode,
            "stdout": sonuc.stdout[-3000:],
            "stderr": sonuc.stderr[-1000:] if sonuc.stderr else "",
            "sure_sn": round((bitis - baslangic).total_seconds(), 2),
            "basarili": sonuc.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "hedef": hedef,
            "cikis_kodu": -1,
            "stdout": "TIMEOUT",
            "stderr": "",
            "sure_sn": 120,
            "basarili": False,
        }
    except Exception as e:
        return {
            "hedef": hedef,
            "cikis_kodu": -1,
            "stdout": "",
            "stderr": str(e),
            "sure_sn": 0,
            "basarili": False,
        }


def _satir_say(stdout: str, arama: str) -> str:
    """stdout icinden 'X passed, Y failed' tipinde satiri bulur."""
    for satir in stdout.splitlines():
        if arama in satir:
            return satir.strip()
    return ""


def calistir(verbose: bool = False) -> dict:
    """Tum test gruplarini calistirir, ozet JSON doner."""
    python = _venv_python()
    zaman = datetime.now().isoformat()

    print(f"\n{'='*60}")
    print(f"ReYMeN Saatlik Test — {zaman}")
    print(f"Python: {python}")
    print(f"Kök dizin: {ROOT}")
    print(f"{'='*60}")

    sonuclar = {}

    # 1. test_suite.py (doğrudan Python)
    print("\n[1/3] test_suite.py calisiyor...")
    r = _calistir(python, str(ROOT / "test_suite.py"))
    sonuclar["test_suite"] = r
    # 35/35 formatini parse et
    ozet = _satir_say(r["stdout"], "gecti")
    if not ozet:
        ozet = "gecti/toplam bilgisi yok"
    print(f"      {ozet} (sure: {r['sure_sn']}sn)")
    if verbose and not r["basarili"]:
        print(r["stdout"][-1000:])

    # 2. test_providers.py (pytest)
    print("\n[2/3] test_providers.py calisiyor...")
    r2 = _pytest_calistir(python, "tests/test_providers.py")
    sonuclar["test_providers"] = r2
    ozet2 = _satir_say(r2["stdout"], "passed")
    if not ozet2:
        ozet2 = r2["stdout"].splitlines()[-1] if r2["stdout"].strip() else "cikti yok"
    print(f"      {ozet2} (sure: {r2['sure_sn']}sn)")
    if verbose and not r2["basarili"]:
        print(r2["stdout"][-1000:])

    # 3. tests/ Kategori A (hizli kontrol)
    print("\n[3/3] tests/ klasoru calisiyor...")
    r3 = _pytest_calistir(python, "tests/")
    sonuclar["tests_klasoru"] = r3
    ozet3 = _satir_say(r3["stdout"], "passed")
    if not ozet3:
        ozet3 = r3["stdout"].splitlines()[-1] if r3["stdout"].strip() else "cikti yok"
    print(f"      {ozet3} (sure: {r3['sure_sn']}sn)")
    if verbose and not r3["basarili"]:
        print(r3["stdout"][-2000:])

    # Genel ozet
    hepsi_gecti = all(v["basarili"] for v in sonuclar.values())
    durum = "BASARILI" if hepsi_gecti else "HATALI"

    ozet_rapor = {
        "zaman": zaman,
        "python": python,
        "durum": durum,
        "sonuclar": {
            k: {
                "basarili": v["basarili"],
                "sure_sn": v["sure_sn"],
                "cikis_kodu": v["cikis_kodu"],
            }
            for k, v in sonuclar.items()
        },
    }

    # Log dosyasina kaydet
    log_dosya = LOG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_dosya.write_text(
        json.dumps(ozet_rapor, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\n{'='*60}")
    print(f"SONUC: {durum}")
    for k, v in ozet_rapor["sonuclar"].items():
        isaret = "OK " if v["basarili"] else "FAIL"
        print(f"  [{isaret}] {k} ({v['sure_sn']}sn)")
    print(f"Log: {log_dosya}")
    print(f"{'='*60}\n")

    return ozet_rapor


if __name__ == "__main__":
    verbose = "--verbose" in sys.argv
    rapor = calistir(verbose=verbose)
    sys.exit(0 if rapor["durum"] == "BASARILI" else 1)
