#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reymen_coverage_runner.py — ReYMeN Coverage Olcum Sistemi
=========================================================
pytest-cov ile entegre, HTML/XML/JSON rapor uretir.

Kullanim:
    python tests/reymen_coverage_runner.py                 # Tum proje coverage
    python tests/reymen_coverage_runner.py --quick         # Hizli (sadece core moduller)
    python tests/reymen_coverage_runner.py --html          # HTML rapor
    python tests/reymen_coverage_runner.py --open          # HTML rapor + browser'da ac
"""

import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COVERAGE_DIR = ROOT / "tests" / "coverage_html"

RENK = {
    "yesil": "\033[92m",
    "kirmizi": "\033[91m",
    "sari": "\033[93m",
    "mavi": "\033[94m",
    "mor": "\033[95m",
    "cyan": "\033[96m",
    "koyu": "\033[90m",
    "kalın": "\033[1m",
    "son": "\033[0m",
}


def renkli(yazi, *renkler):
    prefix = "".join(RENK.get(r, r) for r in renkler)
    return f"{prefix}{yazi}{RENK['son']}"


def coverage_calistir(quick=False, html=False, xml=False, json_rapor=False):
    """coverage run ile olcum yap (pytest-cov yerine dogrudan coverage kullan)."""

    if quick:
        kaynaklar = ["motor", "beyin", "main",
                     "conversation_loop", "session_db",
                     "agent/", "tools/"]
    else:
        kaynaklar = ["."]

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["COVERAGE_FILE"] = str(ROOT / ".coverage")

    # coverage run: pytest-cov'den daha guvenilir (top-level import sorunu yok)
    if quick:
        test_hedefi = "test_suite.py"
    else:
        test_hedefi = "test_suite.py tests/"

    args = [sys.executable, "-m", "coverage", "run",
            "--source=" + ",".join(kaynaklar),
            "--omit=*/tests/*,*/venv/*,*/venv2/*,*/__pycache__/*,*/.git/*,*/node_modules/*",
            "-m", "pytest", test_hedefi, "-q", "--tb=short", "-x"]

    print(f"\n{renkli('ReYMeN Coverage Olcum', 'kalın', 'cyan')}")
    print(f"{renkli('='*55, 'koyu')}")
    print(f"  Kaynak: {', '.join(kaynaklar)}")
    print(f"  Mod: {'Hizli' if quick else 'Tam'}")
    print(f"{renkli('='*55, 'koyu')}\n")

    basla = time.time()

    # 1) coverage run ile testleri calistir
    rc = subprocess.run(args, cwd=str(ROOT), capture_output=True, text=True,
                        timeout=600, env=env)
    sure_test = round(time.time() - basla, 2)

    # 2) coverage report al
    report_args = [sys.executable, "-m", "coverage", "report", "--show-missing",
                   "--omit=*/tests/*,*/venv/*,*/venv2/*,*/__pycache__/*,*/.git/*,*/node_modules/*"]
    if html:
        COVERAGE_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "-m", "coverage", "html",
                       f"--directory={COVERAGE_DIR}"], cwd=str(ROOT),
                       capture_output=True, timeout=30)

    report_rc = subprocess.run(report_args, cwd=str(ROOT), capture_output=True, text=True, timeout=30)

    sure = round(time.time() - basla, 2)
    raw = report_rc.stdout + report_rc.stderr

    # Ciktiyi goster
    for satir in raw.split("\n"):
        s = satir.strip()
        if not s:
            continue
        if "TOTAL" in s:
            print(f"  {renkli(s, 'kalın', 'cyan')}")
        elif "%" in s:
            yuzde = re.search(r"(\d+)%", s)
            if yuzde:
                r = "yesil" if int(yuzde.group(1)) >= 80 else ("sari" if int(yuzde.group(1)) >= 50 else "kirmizi")
                print(f"  {renkli(s, r)}")
            else:
                print(f"  {s}")
        elif not (s.startswith("---") or s.startswith("==") or s.startswith("..") or "warnings" in s.lower()):
            pass  # Sadece coverage ciktisini goster

    print(f"\n{renkli('─'*55, 'koyu')}")
    print(f"  Sure: {renkli(f'{sure}s', 'sari')}")
    print(f"  Durum: {renkli('OK', 'yesil') if rc.returncode == 0 else renkli('FAIL', 'kirmizi')}")

    m = re.search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%", raw)
    if m:
        print(f"  Statement: {m.group(1)}, Kapsanmayan: {m.group(2)}, "
              f"Coverage: {renkli(f'%{m.group(5)}', 'yesil' if int(m.group(5)) >= 80 else 'sari')}")

    if html:
        html_path = COVERAGE_DIR / "index.html"
        if html_path.exists():
            print(f"  HTML: file:///{html_path.resolve().as_posix()}")

    # JSON sonucu kaydet
    cov_veri = {
        "tarih": datetime.datetime.now().isoformat(),
        "sure": sure,
        "basari": rc.returncode == 0,
    }
    if m:
        cov_veri.update({
            "statement": int(m.group(1)),
            "kacirilan": int(m.group(2)),
            "cover_yuzde": int(m.group(5)),
        })
    # Modul bazinda
    moduller = []
    for satir in raw.split("\n"):
        mm = re.match(r"^\s*(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)%\s*$", satir)
        if mm and mm.group(1).strip() != "TOTAL":
            moduller.append({
                "modul": mm.group(1).strip(),
                "statement": int(mm.group(2)),
                "kacirilan": int(mm.group(3)),
                "cover": int(mm.group(5)),
            })
    cov_veri["moduller"] = moduller
    json_yol = ROOT / "tests" / "son_coverage.json"
    with open(json_yol, "w", encoding="utf-8") as f:
        json.dump(cov_veri, f, indent=2, ensure_ascii=False)
    print(f"  JSON: {json_yol}")

    print(f"{renkli('='*55, 'koyu')}\n")
    return rc.returncode


def main():
    import argparse
    parser = argparse.ArgumentParser(description="ReYMeN Coverage Olcum Sistemi")
    parser.add_argument("--quick", action="store_true", help="Hizli mod")
    parser.add_argument("--html", action="store_true", help="HTML rapor")
    parser.add_argument("--xml", action="store_true", help="XML rapor")
    parser.add_argument("--json", action="store_true", help="JSON rapor")
    parser.add_argument("--open", action="store_true", help="Browser'da ac")
    args = parser.parse_args()

    rc = coverage_calistir(quick=args.quick, html=args.html or args.open,
                           xml=args.xml, json_rapor=args.json)

    if args.open:
        html_path = COVERAGE_DIR / "index.html"
        if html_path.exists():
            subprocess.run(["cmd", "/c", "start", "", str(html_path)], check=False)
    return rc


if __name__ == "__main__":
    sys.exit(main())
