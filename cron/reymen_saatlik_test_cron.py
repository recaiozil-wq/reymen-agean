#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reymen_saatlik_test_cron.py — ReYMeN Saatlik Test Cron Script'i
ReYMeN ~/.hermes/scripts/ altina kopyalanir.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(r"C:\Users\marko\OneDrive\Desktop\Reymen Proje\hermes_projesi")
RUNNER = ROOT / "tests" / "reymen_test_runner.py"
COVERAGE_RUNNER = ROOT / "tests" / "reymen_coverage_runner.py"
RAPOR_JSON = ROOT / "tests" / "son_test_raporu.json"
COV_JSON = ROOT / "tests" / "son_coverage.json"


def calistir(komut, timeout=300):
    try:
        sonuc = subprocess.run(
            komut, capture_output=True, text=True, timeout=timeout, cwd=str(ROOT)
        )
        return sonuc.stdout, sonuc.stderr, sonuc.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except Exception as e:
        return "", str(e), -1


def main():
    basla = time.time()

    # 1. HIZLI TEST (core + pytest)
    stdout, stderr, rc = calistir(
        [sys.executable, "-u", str(RUNNER), "--quick", "--json", str(RAPOR_JSON)],
        timeout=400,
    )

    # 2. COVERAGE (hizli)
    cov_out, cov_err, cov_rc = calistir(
        [sys.executable, "-u", str(COVERAGE_RUNNER), "--quick", "--json"],
        timeout=300,
    )

    # 3. RAPOR
    test_veri = {"durum": "bilinmiyor", "gecen": 0, "kalan": 0, "oran": 0}
    if RAPOR_JSON.exists():
        with open(RAPOR_JSON) as f:
            test_veri = json.load(f)

    cov_veri = {"cover_yuzde": 0, "statement": 0}
    if COV_JSON.exists():
        with open(COV_JSON) as f:
            cov_veri = json.load(f)

    sure = round(time.time() - basla, 1)
    gecen = test_veri.get("gecen_test", 0)
    kalan = test_veri.get("kalan_test", 0)
    oran = test_veri.get("oran", 0)
    cover = cov_veri.get("cover_yuzde", 0)
    dosya_say = test_veri.get("dosya_sayisi", 0)

    durum = "✅" if kalan == 0 else "❌"

    print(f"{durum} ReYMeN Test | {time.strftime('%H:%M')}")
    print(f"  Test: {gecen}/{gecen + kalan} gecti, %{oran}")
    print(f"  Coverage: %{cover} ({cov_veri.get('statement', 0)} stmt)")
    print(f"  Dosya: {dosya_say} | Sure: {sure}s")

    if kalan > 0:
        print(f"\nHatalar:")
        for h in test_veri.get("hatalar", [])[:5]:
            print(f"  ✗ {h.get('dosya', '?')}")

    if stderr and "TIMEOUT" in stderr:
        print(f"\n⚠️ TIMEOUT - bazi testler zaman asti")

    print(f"\nKategoriler:")
    for kat in test_veri.get("kategoriler", []):
        ikon = "✅" if kat.get("basari", False) else "❌"
        print(f"  {ikon} {kat.get('ad', '?')}: {kat.get('gecen', 0)}/{kat.get('toplam', 0)}")

    print(f"\n#reymen #test #{time.strftime('%d-%m-%Y')}")


if __name__ == "__main__":
    main()
