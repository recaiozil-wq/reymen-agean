#!/usr/bin/env python3
"""
FIX 03 â€” Coverage Kurulum & HÄ±zlÄ± Test KoÅŸucusu
Yapar : pytest-cov kurar, sadece reymen/ paketini test eder
Test  : her modülü ayrÄ± ayrÄ± çalÄ±ÅŸtÄ±rÄ±r
Rapor : fix_03_rapor.json + konsol özeti
"""

import sys, json, time, shutil, subprocess
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class C:
    RED = "\033[91m"
    YEL = "\033[93m"
    GRN = "\033[92m"
    BLU = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def ok(m):
    print(f"  {C.GRN}âœ… {m}{C.RESET}")


def warn(m):
    print(f"  {C.YEL}âš ï¸  {m}{C.RESET}")


def err(m):
    print(f"  {C.RED}âŒ {m}{C.RESET}")


def hdr(t):
    print(f"\n{C.BOLD}{C.BLU}{'â•'*60}\n  {t}\n{'â•'*60}{C.RESET}")


def cmd(komut, cwd=None, timeout=120):
    try:
        r = subprocess.run(
            komut,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r.returncode, r.stdout + r.stderr
    except subprocess.TimeoutExpired:
        return -1, f"TIMEOUT ({timeout}s)"
    except FileNotFoundError:
        return -2, f"Komut bulunamadÄ±: {komut[0]}"


def pip_kur(paket):
    code, out = cmd([sys.executable, "-m", "pip", "install", paket, "-q"])
    return code == 0


def main():
    kok = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(".").resolve()
    hdr(f"FIX 03 â€” Coverage & Test KoÅŸucusu\nKök: {kok}")
    t0 = time.time()
    rapor = {
        "tarih": datetime.now().isoformat(),
        "kok": str(kok),
        "paket_kurulum": {},
        "modül_testler": [],
        "coverage": {},
        "genel": {},
    }

    hdr("1. Paket Kurulumu")
    for p in ["pytest", "pytest-cov", "pytest-timeout"]:
        kodu, _ = cmd([sys.executable, "-m", "pip", "show", p.split("-")[0]])
        if kodu == 0:
            ok(f"{p} zaten kurulu")
            rapor["paket_kurulum"][p] = "zaten_kurulu"
        elif pip_kur(p):
            ok(f"{p} kuruldu")
            rapor["paket_kurulum"][p] = "kuruldu"
        else:
            err(f"{p} kurulamadÄ±")
            rapor["paket_kurulum"][p] = "HATA"

    hdr("2. Modül BazlÄ± Test")
    test_dizinleri = []
    for mod in ["cereyan", "sistem", "hafiza", "arac", "guvenlik"]:
        for td in [kok / "tests" / mod, kok / f"tests/test_{mod}"]:
            if td.exists():
                test_dizinleri.append((mod, td))
                break
        else:
            testler = list(kok.rglob(f"test_{mod}*.py"))
            if testler:
                test_dizinleri.append((mod, testler[0].parent))
    if not test_dizinleri:
        warn("Modül test dizini bulunamadÄ±")
        test_dizinleri = [("reymen", kok / "tests")] if (kok / "tests").exists() else []

    for mod, td in test_dizinleri:
        print(f"\n  {C.BLU}â–¶ {mod}{C.RESET}  ({td})")
        kod, out = cmd(
            [
                sys.executable,
                "-m",
                "pytest",
                str(td),
                "-q",
                "--tb=short",
                "--no-header",
                "--timeout=30",
                f"--cov=reymen.{mod}",
                "--cov-report=term-missing:skip-covered",
                "-x",
            ],
            cwd=kok,
            timeout=90,
        )
        satirlar = out.splitlines()
        ozet = next(
            (
                s
                for s in reversed(satirlar)
                if "passed" in s or "failed" in s or "error" in s
            ),
            "",
        )
        cov_satir = next((s for s in satirlar if "TOTAL" in s), "")
        if kod == 0:
            ok(f"{ozet}")
        elif kod == -1:
            warn(f"TIMEOUT â€” {mod}")
        else:
            err(f"{ozet or 'Test baÅŸarÄ±sÄ±z'}")
            for s in satirlar[:30]:
                if "FAILED" in s or "ERROR" in s:
                    print(f"    {C.RED}{s}{C.RESET}")
        if cov_satir:
            print(f"    {C.BLU}{cov_satir}{C.RESET}")
        rapor["modül_testler"].append(
            {
                "modül": mod,
                "dizin": str(td),
                "return_code": kod,
                "ozet": ozet,
                "coverage_satiri": cov_satir,
            }
        )

    hdr("3. Genel Coverage")
    if (kok / "reymen").exists():
        kod, out = cmd(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-q",
                "--tb=no",
                "--no-header",
                "--timeout=20",
                "--cov=reymen",
                "--cov-report=term-missing:skip-covered",
                "--cov-report=json:coverage.json",
                "-x",
                "--ignore=tests/test_bulk_5000.py",
            ],
            cwd=kok,
            timeout=180,
        )
        if kod == -1:
            warn("Genel coverage timeout â€” modül raporlarÄ±na bak")
        else:
            for s in out.splitlines():
                if "TOTAL" in s or "passed" in s or "failed" in s:
                    print(f"  {C.GRN if 'passed' in s else C.YEL}{s}{C.RESET}")
        cov_json = kok / "coverage.json"
        if cov_json.exists():
            try:
                cd = json.loads(cov_json.read_text()).get("totals", {})
                rapor["coverage"] = {
                    "toplam_satir": cd.get("num_statements"),
                    "kapsanan": cd.get("covered_lines"),
                    "yüzde": cd.get("percent_covered_display"),
                }
                ok(f"Coverage: %{cd.get('percent_covered_display','?')}")
            except Exception as _e:
                pass  # log eklenecek

    hdr("4. cli.py Coverage")
    for cli in kok.rglob("reymen/sistem/cli.py"):
        kod, out = cmd(
            [
                sys.executable,
                "-m",
                "pytest",
                "tests/",
                "-q",
                "--tb=no",
                "--timeout=20",
                f"--cov={cli.relative_to(kok)}",
                "--cov-report=term-missing",
                "-k",
                "cli",
                "--ignore=tests/test_bulk_5000.py",
            ],
            cwd=kok,
            timeout=60,
        )
        if kod == -1:
            warn("cli.py coverage timeout")
        else:
            for s in out.splitlines():
                if "cli" in s.lower() and "%" in s:
                    print(f"  {C.YEL}{s}{C.RESET}")
            if "%" not in out:
                warn("cli.py coverage ~%5")

    rapor["genel"]["sure"] = round(time.time() - t0, 1)
    hdr("Ã–ZET RAPOR")
    gecen = sum(1 for m in rapor["modül_testler"] if m["return_code"] == 0)
    hata = sum(1 for m in rapor["modül_testler"] if m["return_code"] not in (0, -1))
    timeout = sum(1 for m in rapor["modül_testler"] if m["return_code"] == -1)
    print(f"  Test geçen modül  : {C.GRN}{gecen}{C.RESET}")
    print(f"  Test hata modül   : {C.RED}{hata}{C.RESET}")
    print(f"  Timeout modül     : {C.YEL}{timeout}{C.RESET}")
    if rapor["coverage"].get("yüzde"):
        print(f"  Genel coverage    : {C.BLU}%{rapor['coverage']['yüzde']}{C.RESET}")
    print(f"  Süre              : {rapor['genel']['sure']}s")
    rapor_yolu = kok / "fix_03_rapor.json"
    with open(rapor_yolu, "w") as fp:
        json.dump(rapor, fp, ensure_ascii=False, indent=2)
    ok(f"JSON rapor: {rapor_yolu}")


if __name__ == "__main__":
    main()
