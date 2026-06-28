#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
reymen_test_runner.py — ReYMeN Test Otomasyon Sistemi
======================================================
ReYMeN'in 30K test altyapisina benzer, ReYMeN'e ozel test orkestratoru.

Ozellikler:
  - Otomatik test kesfi (root ve tests/ altindaki tum test_*.py)
  - Kategorilere ayirma: core, pytest, reference, integration
  - Batch halinde calistirma + timeout yonetimi
  - Renkli terminal ciktisi
  - JSON rapor (parcalanabilir)
  - HTML rapor (insan okunabilir)
  - Cron ile entegrasyon

Kullanim:
    python tests/reymen_test_runner.py                 # Tum testler
    python tests/reymen_test_runner.py --core           # Sadece core testler
    python tests/reymen_test_runner.py --pytest         # Sadece pytest testler
    python tests/reymen_test_runner.py --reference      # Sadece ReYMeN reference testler
    python tests/reymen_test_runner.py --quick          # Hizli mod (core + pytest)
    python tests/reymen_test_runner.py --html           # HTML rapor da uret
    python tests/reymen_test_runner.py --json rapor.json # JSON cikti
    python tests/reymen_test_runner.py --watch          # Dosya degisikligi bekle
    python tests/reymen_test_runner.py --cron           # Cron modu (detayli rapor)
"""

import datetime
import json
import os
import re
import subprocess
import sys
import time
import traceback
from pathlib import Path


# Yeni marker'larla uyumlu test secenekleri
MARKER_SECENEKLERI = {
    "smoke": "en kritik yol — her commit oncesi",
    "unit": "birim testi (izole, hizli)",
    "cua": "Computer Use Agent testi",
    "network": "ag baglantisi gerektiren test",
    "slow": "yavas calisan test",
    "integration": "entegrasyon testi",
}

# ──────────────────────────────────────────────
# YAPILANDIRMA
# ──────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
TESTS_DIR = ROOT / "tests"

# Kategoriler
KATEGORILER = {
    "core": {
        "aciklama": "ReYMeN core testleri (kokteki test_*.py)",
        "dizin": ROOT,
        "desen": r"^test_(?!batch_10|harvest)_.*\.py$|^test_suite\.py$|^test_providers\.py$",
        "oncelik": 1,
    },
    "pytest": {
        "aciklama": "ReYMeN pytest testleri (tests/ alti)",
        "dizin": TESTS_DIR,
        "desen": r"^test_.*\.py$",
        "oncelik": 2,
        "hariç": ["ReYMeN_reference"],
    },
    "reference": {
        "aciklama": "ReYMeN reference testleri (tests/ReYMeN_reference/)",
        "dizin": TESTS_DIR / "ReYMeN_reference",
        "desen": r"^test_.*\.py$",
        "oncelik": 3,
    },
    "all": {
        "aciklama": "Tum testler",
        "oncelik": 4,
    },
}

# Renkler (Windows uyumlu)
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

# ──────────────────────────────────────────────
# YARDIMCI FONKSIYONLAR
# ──────────────────────────────────────────────


def renkli(yazi, *renkler):
    """Metni renklendir."""
    prefix = "".join(RENK.get(r, r) for r in renkler)
    return f"{prefix}{yazi}{RENK['son']}"


def test_dosyalarini_bul(dizin, desen, hariç=None):
    """Belirtilen dizindeki test dosyalarini bul."""
    dosyalar = []
    for f in sorted(dizin.glob("test_*.py")):
        if hariç:
            # Dizinden hariç tutulanlari kontrol et
            parent_name = f.relative_to(dizin).parts[0]
            if parent_name in hariç:
                continue
        if re.match(desen, f.name):
            dosyalar.append(f)
    return dosyalar


def komut_calistir(komut, timeout=300, workdir=None):
    """Bir komutu calistir ve ciktisini al."""
    basla = time.time()
    try:
        sonuc = subprocess.run(
            komut,
            cwd=workdir or str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False,
        )
        sure = time.time() - basla
        return {
            "exit_code": sonuc.returncode,
            "stdout": sonuc.stdout,
            "stderr": sonuc.stderr,
            "sure": round(sure, 2),
            "basarili": sonuc.returncode == 0,
            "timeout": False,
        }
    except subprocess.TimeoutExpired:
        sure = time.time() - basla
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"TIMEOUT ({sure:.0f}s)",
            "sure": round(sure, 2),
            "basarili": False,
            "timeout": True,
        }
    except FileNotFoundError as e:
        return {
            "exit_code": -1,
            "stdout": "",
            "stderr": f"Komut bulunamadi: {e}",
            "sure": 0,
            "basarili": False,
            "timeout": False,
        }


def sayi_ayristir(cikti, desen):
    """Regex ile test ciktisindan sayi al."""
    m = re.search(desen, cikti)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return m.group(1)
    return "?"


# ──────────────────────────────────────────────
# TEST KOSUCULARI
# ──────────────────────────────────────────────


def run_core_testler(dosyalar):
    """Kokteki test_*.py dosyalarini sirayla calistir."""
    sonuclar = []
    for f in dosyalar:
        print(f"  {renkli('▶', 'mavi')} {f.name}... ", end="", flush=True)
        sonuc = komut_calistir(
            [sys.executable, "-u", str(f)], timeout=300, workdir=str(ROOT)
        )
        if sonuc["basarili"]:
            # test_suite.py formatindan sayilari cikar
            m = re.search(r"Sonuc:\s*(\d+)/(\d+)", sonuc["stdout"])
            gecen = m.group(1) if m else "?"
            toplam = m.group(2) if m else "?"
            print(
                renkli(f"OK", "yesil")
                + f" ({gecen}/{toplam}, {sonuc['sure']}s)"
            )
        else:
            print(renkli(f"FAIL", "kirmizi") + f" ({sonuc['sure']}s)")
            if sonuc["timeout"]:
                print(f"    {renkli('TIMEOUT', 'sari')}")
            else:
                # Ilk 3 hata satirini goster
                hata = sonuc.get("stderr", "") or sonuc.get("stdout", "")
                satirlar = hata.strip().split("\n")[-8:]
                for s in satirlar:
                    print(f"    {renkli('!', 'kirmizi')} {s}")
        sonuclar.append(
            {
                "dosya": str(f),
                "ad": f.name,
                "basari": sonuc["basarili"],
                "sure": sonuc["sure"],
                "cikti": sonuc["stdout"],
                "hata": sonuc["stderr"],
            }
        )
    return sonuclar


def run_pytest_testler(dosyalar, extra_args=None, marker=None):
    """Pytest ile test dosyalarini calistir."""
    if not dosyalar:
        return {"toplam": 0, "gecen": 0, "kalan": 0, "sure": 0, "detay": []}

    args = [sys.executable, "-m", "pytest", "-v"]
    if marker:
        args.extend(["-m", marker])
    if extra_args:
        args.extend(extra_args)
    args.extend(str(f) for f in dosyalar)

    sonuc = komut_calistir(args, timeout=600, workdir=str(ROOT))

    # Sonuclari parse et
    gecen = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+passed")
    kalan = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+failed")
    uyari = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+warning")
    atlanan = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+skipped")
    hata = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+errors?")

    return {
        "toplam": gecen,
        "gecen": gecen,
        "kalan": kalan,
        "uyari": uyari,
        "atlanan": atlanan,
        "hata": hata,
        "sure": sonuc["sure"],
        "basari": sonuc["basarili"],
        "cikti": sonuc["stdout"],
        "detay": [],
    }


def run_reference_testler(dizin, max_files=50):
    """ReYMeN reference testlerini batch halinde calistir."""
    test_dosyalari = sorted(dizin.rglob("test_*.py"))
    if not test_dosyalari:
        return {"toplam": 0, "gecen": 0, "kalan": 0, "sure": 0, "batch": []}

    # Batch'lere bol
    batch_boyut = 10
    batchler = [
        test_dosyalari[i : i + batch_boyut]
        for i in range(0, len(test_dosyalari), batch_boyut)
    ][: max_files // batch_boyut + 1]

    sonuclar = []
    toplam_sure = 0
    toplam_gecen = 0
    toplam_kalan = 0

    for i, batch in enumerate(batchler):
        print(
            f"  {renkli('Reference Batch', 'mor')} {i+1}/{len(batchler)} ({len(batch)} dosya)... ",
            end="",
            flush=True,
        )

        # Her batch 60 saniye timeout
        sonuc = komut_calistir(
            [sys.executable, "-m", "pytest", "-x", "-q", "--tb=short"]
            + [str(f) for f in batch],
            timeout=60,
            workdir=str(ROOT),
        )

        gecen = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+passed")
        kalan = sayi_ayristir(sonuc["stdout"], r"(\d+)\s+failed")

        toplam_gecen += int(gecen) if gecen != "?" else 0
        toplam_kalan += int(kalan) if kalan != "?" else 0
        toplam_sure += sonuc["sure"]

        durum = renkli("OK", "yesil") if sonuc["basarili"] else renkli("FAIL", "kirmizi")
        print(f"{durum} (g:{gecen} k:{kalan} {sonuc['sure']}s)")

        sonuclar.append(
            {
                "batch_no": i + 1,
                "dosyalar": [str(f) for f in batch],
                "basari": sonuc["basarili"],
                "sure": sonuc["sure"],
                "cikti": sonuc["stdout"][:500] if not sonuc["basarili"] else "",
            }
        )

    return {
        "toplam": len(test_dosyalari[:max_files]),
        "batch_sayisi": len(batchler),
        "gecen": toplam_gecen,
        "kalan": toplam_kalan,
        "sure": round(toplam_sure, 2),
        "batch": sonuclar,
    }


# ──────────────────────────────────────────────
# RAPORLAMA
# ──────────────────────────────────────────────


def json_rapor_uret(sonuc, dosya_yolu):
    """JSON rapor dosyasi olustur."""
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        json.dump(sonuc, f, indent=2, ensure_ascii=False)
    print(f"\n{renkli('JSON rapor:', 'koyu')} {dosya_yolu}")


def html_rapor_uret(sonuc, dosya_yolu):
    """Insan okunabilir HTML rapor olustur."""
    renk = lambda g: "#22c55e" if g else "#ef4444"

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ReYMeN Test Raporu — {sonuc.get("tarih", "?")}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
         background: #0f172a; color: #e2e8f0; padding: 2rem; }}
  h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; color: #f8fafc; }}
  .meta {{ color: #94a3b8; font-size: 0.9rem; margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: #1e293b; border-radius: 12px; padding: 1.2rem; }}
  .card .label {{ font-size: 0.8rem; color: #64748b; text-transform: uppercase; }}
  .card .value {{ font-size: 2rem; font-weight: 700; margin-top: 0.3rem; }}
  table {{ width: 100%; border-collapse: collapse; margin-top: 1.5rem; }}
  th {{ text-align: left; padding: 0.6rem 1rem; background: #1e293b; color: #94a3b8;
        font-size: 0.8rem; text-transform: uppercase; }}
  td {{ padding: 0.6rem 1rem; border-bottom: 1px solid #1e293b; }}
  .ok {{ color: #22c55e; }} .fail {{ color: #ef4444; }} .warn {{ color: #f59e0b; }}
  .progress {{ height: 8px; background: #334155; border-radius: 4px; margin: 1rem 0; overflow: hidden; }}
  .progress-bar {{ height: 100%; background: linear-gradient(90deg, #22c55e, #16a34a);
                   border-radius: 4px; transition: width 0.5s; }}
  footer {{ margin-top: 2rem; color: #475569; font-size: 0.8rem; text-align: center; }}
  pre {{ background: #1e293b; padding: 0.5rem; border-radius: 6px; font-size: 0.8rem;
         max-height: 200px; overflow: auto; color: #94a3b8; }}
  .header {{ display: flex; justify-content: space-between; align-items: center; }}
  .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
            font-size: 0.8rem; font-weight: 600; }}
  .badge-ok {{ background: #166534; color: #86efac; }}
  .badge-fail {{ background: #7f1d1d; color: #fca5a5; }}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>🧪 ReYMeN Test Raporu</h1>
    <p class="meta">{sonuc.get("tarih", "?")} &middot; {sonuc.get("sure", "?")}s &middot; {sonuc.get("kategori", "tum")}</p>
  </div>
  <div>
    <span class="badge {'badge-ok' if sonuc.get('genel_durum', False) else 'badge-fail'}">
      {'TUM TESTLER GECTI' if sonuc.get('genel_durum', False) else 'BAZILARI KALDI'}
    </span>
  </div>
</div>

<div class="grid">
  <div class="card">
    <div class="label">Test Dosyasi</div>
    <div class="value">{sonuc.get("dosya_sayisi", 0)}</div>
  </div>
  <div class="card">
    <div class="label">Gecen</div>
    <div class="value" style="color:{renk(True)}">{sonuc.get("gecen_test", 0)}</div>
  </div>
  <div class="card">
    <div class="label">Kalan</div>
    <div class="value" style="color:{renk(False)}">{sonuc.get("kalan_test", 0)}</div>
  </div>
  <div class="card">
    <div class="label">Basari Orani</div>
    <div class="value" style="color:{renk(sonuc.get('oran', 0) > 80)}">%{sonuc.get("oran", 0)}</div>
  </div>
</div>

<div class="progress">
  <div class="progress-bar" style="width:{sonuc.get('oran', 0)}%"></div>
</div>

<h2>Kategori Detayi</h2>
<table>
<tr><th>Kategori</th><th>Durum</th><th>Gecen</th><th>Kalan</th><th>Sure</th></tr>
"""

    for kat in sonuc.get("kategoriler", []):
        durum = "ok" if kat.get("basari", False) else "fail"
        sembol = "✅" if kat.get("basari", False) else "❌"
        html += f"""<tr>
  <td><strong>{kat.get("ad", "?")}</strong></td>
  <td class="{durum}">{sembol}</td>
  <td>{kat.get("gecen", 0)}</td>
  <td>{kat.get("kalan", 0)}</td>
  <td>{kat.get("sure", 0)}s</td>
</tr>"""

    html += """</table>"""

    # Hata detayi varsa
    hatalar = sonuc.get("hatalar", [])
    if hatalar:
        html += """<h2>Kalan Testler (Hata Detayi)</h2><table>
<tr><th>Dosya</th><th>Hata</th></tr>"""
        for h in hatalar:
            html += f"<tr><td>{h.get('dosya', '?')}</td><td><pre>{h.get('hata', '?')}</pre></td></tr>"
        html += "</table>"

    html += f"""
<footer>
  ReYMeN Test Runner &middot; {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
</footer>
</body>
</html>"""

    with open(dosya_yolu, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"{renkli('HTML rapor:', 'koyu')} {dosya_yolu}")


def rapor_ozetle(sonuc):
    """Terminale ozet yazdir."""
    print(f"\n{'='*55}")
    print(f"  {renkli('ReYMeN Test Sonucu', 'kalın', 'cyan')}")
    print(f"  Kategori: {renkli(sonuc.get('kategori', 'tum'), 'mavi')}")
    print(f"  Tarih: {sonuc.get('tarih', '?')}")
    sure_str = f"{sonuc.get('sure', 0)}s"
    print(f"  Sure: {renkli(sure_str, 'sari')}")
    print(f"{'='*55}")

    gecen = sonuc.get("gecen_test", 0)
    kalan = sonuc.get("kalan_test", 0)
    toplam = gecen + kalan
    oran = sonuc.get("oran", 0)

    if toplam > 0:
        print(f"  Test dosyasi: {sonuc.get('dosya_sayisi', 0)}")
        print(f"  Gecen: {renkli(str(gecen), 'yesil')}")
        print(f"  Kalan: {renkli(str(kalan), 'kirmizi') if kalan > 0 else renkli('0', 'yesil')}")
        print(f"  Basari: {renkli(f'%{oran}', 'yesil' if oran >= 90 else 'sari')}")

        # Progress bar
        bar_uzunluk = 30
        dolu = int(bar_uzunluk * oran / 100)
        bos = bar_uzunluk - dolu
        bar = f"[{'█' * dolu}{'░' * bos}]"
        print(f"  {bar}")

    print(f"{'='*55}")

    # Kategoriler
    for kat in sonuc.get("kategoriler", []):
        durum_renk = "yesil" if kat.get("basari", False) else "kirmizi"
        print(
            f"  {renkli('▸', durum_renk)} {kat.get('ad', '?')}: "
            f"{kat.get('gecen', 0)}/{kat.get('toplam', 0)} gecti, "
            f"{kat.get('kalan', 0)} kaldi, "
            f"{kat.get('sure', 0)}s"
        )

    # Hatalar
    hatalar = sonuc.get("hatalar", [])
    if hatalar:
        print(f"\n  {renkli('KALAN TESTLER:', 'kirmizi', 'kalın')}")
        for h in hatalar[:10]:  # Ilk 10 hatayi goster
            print(f"  {renkli('✗', 'kirmizi')} {h.get('dosya', '?')}")
            if h.get("hata"):
                for s in h["hata"].strip().split("\n")[:3]:
                    print(f"    {renkli('└', 'koyu')} {s.strip()}")
        if len(hatalar) > 10:
            print(f"  {renkli(f'... ve {len(hatalar)-10} hata daha', 'koyu')}")

    if sonuc.get("genel_durum", False):
        print(f"\n  {renkli('TUM TESTLER GECTI! ✅', 'yesil', 'kalın')}")
    else:
        print(f"\n  {renkli('BAZILARI KALDI ❌', 'kirmizi', 'kalın')}")

    return sonuc.get("genel_durum", False)


# ──────────────────────────────────────────────
# ANA ORKESTRATOR
# ──────────────────────────────────────────────


def ana_calistir(kategori="all", html_rapor=False, json_yol=None, cron_mod=False, marker_filtre=None):
    """Ana test orkestratoru."""
    basla = time.time()

    sonuc = {
        "tarih": datetime.datetime.now().isoformat(),
        "kategori": kategori,
        "genel_durum": True,
        "dosya_sayisi": 0,
        "gecen_test": 0,
        "kalan_test": 0,
        "sure": 0,
        "oran": 0,
        "kategoriler": [],
        "hatalar": [],
        "detay": {},
    }

    print(f"\n{renkli('ReYMeN Test Runner v2.0', 'kalın', 'cyan')}")
    print(f"{renkli('='*55, 'koyu')}")
    print(f"  Kategori: {renkli(kategori, 'mavi')}")
    print(f"  Basladi: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{renkli('='*55, 'koyu')}\n")

    # ── CORE TESTLER ──
    if kategori in ("all", "core", "quick"):
        print(renkli('▸ CORE TESTLER', 'kalın', 'cyan'))
        core_dosyalar = test_dosyalarini_bul(
            KATEGORILER["core"]["dizin"],
            KATEGORILER["core"]["desen"],
        )
        print(f"  Bulunan: {len(core_dosyalar)} dosya\n")

        core_sonuc = run_core_testler(core_dosyalar)
        core_gecen = sum(1 for s in core_sonuc if s["basari"])
        core_kalan = sum(1 for s in core_sonuc if not s["basari"])
        core_sure = round(sum(s["sure"] for s in core_sonuc), 2)

        sonuc["kategoriler"].append({
            "ad": "core",
            "basari": core_kalan == 0,
            "toplam": len(core_sonuc),
            "gecen": core_gecen,
            "kalan": core_kalan,
            "sure": core_sure,
            "dosyalar": core_sonuc,
        })
        sonuc["dosya_sayisi"] += len(core_sonuc)
        sonuc["gecen_test"] += core_gecen
        sonuc["kalan_test"] += core_kalan
        sonuc["genel_durum"] = sonuc["genel_durum"] and (core_kalan == 0)

        for s in core_sonuc:
            if not s["basari"]:
                sonuc["hatalar"].append({
                    "dosya": s["ad"],
                    "hata": s.get("hata", "")[:300],
                })

        print()

    # ── PYTEST TESTLER ──
    if kategori in ("all", "pytest", "quick"):
        if kategori == "quick":
            # Quick mod: sadece tests/test_*.py (reference haric)
            print(renkli('▸ PYTEST TESTLER (hizli)', 'kalın', 'cyan'))
            pytest_dosyalar = test_dosyalarini_bul(
                KATEGORILER["pytest"]["dizin"],
                KATEGORILER["pytest"]["desen"],
                KATEGORILER["pytest"]["hariç"],
            )
        else:
            print(renkli('▸ PYTEST TESTLER', 'kalın', 'cyan'))
            pytest_dosyalar = test_dosyalarini_bul(
                KATEGORILER["pytest"]["dizin"],
                KATEGORILER["pytest"]["desen"],
                KATEGORILER["pytest"]["hariç"],
            )
        print(f"  Bulunan: {len(pytest_dosyalar)} dosya\n")

        if pytest_dosyalar:
            print("  Testler calistiriliyor... ", end="", flush=True)
            p_sonuc = run_pytest_testler(pytest_dosyalar, ["-x", "--tb=short"], marker=marker_filtre)
            gecen = int(p_sonuc["gecen"]) if p_sonuc["gecen"] != "?" else 0
            kalan = int(p_sonuc["kalan"]) if p_sonuc["kalan"] != "?" else 0

            durum_renk = "yesil" if p_sonuc["basari"] else "kirmizi"
            print(renkli("OK" if p_sonuc["basari"] else "FAIL", durum_renk))

            sonuc["kategoriler"].append({
                "ad": "pytest",
                "basari": p_sonuc["basari"],
                "toplam": len(pytest_dosyalar),
                "gecen": gecen,
                "kalan": kalan,
                "sure": p_sonuc["sure"],
            })
            sonuc["dosya_sayisi"] += len(pytest_dosyalar)
            sonuc["gecen_test"] += gecen
            sonuc["kalan_test"] += kalan
            sonuc["genel_durum"] = sonuc["genel_durum"] and p_sonuc["basari"]

            if not p_sonuc["basari"]:
                sonuc["hatalar"].append({
                    "dosya": "pytest (toplu)",
                    "hata": p_sonuc["cikti"][:500],
                })
        else:
            print(f"  {renkli('(test dosyasi yok)', 'koyu')}")

        print()

    # ── REFERENCE TESTLER ──
    if kategori in ("all", "reference"):
        print(renkli('▸ REFERENCE TESTLER (ReYMeN)', 'kalın', 'cyan'))
        ref_dizin = ROOT / "tests" / "ReYMeN_reference"
        if ref_dizin.exists():
            ref_dosyalar = sorted(ref_dizin.rglob("test_*.py"))
            print(f"  Bulunan: {len(ref_dosyalar)} dosya")

            if cron_mod:
                # Cron modu: hizli referans (ilk 20 dosya)
                print(f"  Cron modu: ilk 20 dosya")
                ref_sonuc = run_reference_testler(ref_dizin, max_files=20)
            else:
                ref_sonuc = run_reference_testler(ref_dizin, max_files=50)

            gecen = ref_sonuc.get("gecen", 0)
            kalan = ref_sonuc.get("kalan", 0)

            sonuc["kategoriler"].append({
                "ad": "reference",
                "basari": kalan == 0,
                "toplam": ref_sonuc.get("toplam", 0),
                "gecen": gecen,
                "kalan": kalan,
                "sure": ref_sonuc.get("sure", 0),
                "batch": ref_sonuc.get("batch", []),
            })
            sonuc["dosya_sayisi"] += ref_sonuc.get("toplam", 0)
            sonuc["gecen_test"] += gecen
            sonuc["kalan_test"] += kalan
            sonuc["genel_durum"] = sonuc["genel_durum"] and (kalan == 0)
        else:
            print(f"  {renkli('(dizin yok: tests/ReYMeN_reference)', 'sari')}")

        print()

    # ── HESAPLAMA ──
    toplam = sonuc["gecen_test"] + sonuc["kalan_test"]
    sonuc["oran"] = round(
        (sonuc["gecen_test"] / toplam * 100) if toplam > 0 else 0, 1
    )
    sonuc["sure"] = round(time.time() - basla, 2)

    # ── RAPOR ──
    print(renkli('─' * 55, 'koyu'))
    rapor_ozetle(sonuc)

    # JSON cikti
    if json_yol:
        json_rapor_uret(sonuc, json_yol)

    # HTML rapor
    if html_rapor:
        html_yol = ROOT / "tests" / "reymen_test_raporu.html"
        html_rapor_uret(sonuc, str(html_yol))
        print(f"  HTML: file:///{html_yol.as_posix()}")

    # Cron modu: JSON dosyaya yaz
    if cron_mod:
        cron_yol = ROOT / "tests" / "son_test_raporu.json"
        json_rapor_uret(sonuc, str(cron_yol))

    return sonuc


# ──────────────────────────────────────────────
# KOMUT SATIRI
# ──────────────────────────────────────────────


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="ReYMeN Test Runner — Otomatik Test Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ornekler:
  %(prog)s                    # Tum testler
  %(prog)s --quick            # Hizli mod (core + pytest)
  %(prog)s --core             # Sadece core testler
  %(prog)s --pytest           # Sadece pytest testler
  %(prog)s --reference        # Sadece reference testler
  %(prog)s --html             # HTML rapor ile
  %(prog)s --json rapor.json  # JSON cikti
  %(prog)s --cron             # Cron modu (hizli reference)
  %(prog)s --watch            # Dosya degisikligi bekle
        """,
    )

    parser.add_argument(
        "--core", action="store_true", help="Sadece core testler"
    )
    parser.add_argument(
        "--pytest", action="store_true", help="Sadece pytest testler"
    )
    parser.add_argument(
        "--reference", action="store_true", help="Sadece reference testler"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Hizli mod (core + pytest)"
    )
    parser.add_argument(
        "--html", action="store_true", help="HTML rapor uret"
    )
    parser.add_argument(
        "--json", type=str, metavar="DOSYA", help="JSON cikti dosyasi"
    )
    parser.add_argument(
        "--cron",
        action="store_true",
        help="Cron modu (detayli olmayan, hizli reference)",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Dosya degisikligi bekle ve tekrar calistir",
    )
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Sadece smoke marker'li testler",
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Sadece unit marker'li testler",
    )
    parser.add_argument(
        "--cua",
        action="store_true",
        help="Sadece CUA marker'li testler",
    )
    parser.add_argument(
        "--marker",
        type=str,
        metavar="MARKER_ADI",
        help="Ozel marker filtresi (ornek: --marker network)",
    )

    args = parser.parse_args()

    # Kategori belirle
    if args.core:
        kategori = "core"
    elif args.pytest:
        kategori = "pytest"
    elif args.reference:
        kategori = "reference"
    elif args.quick:
        kategori = "quick"
    elif args.smoke:
        kategori = "smoke"
    elif args.unit:
        kategori = "unit"
    elif args.cua:
        kategori = "cua"
    elif args.marker:
        kategori = f"marker:{args.marker}"
    else:
        kategori = "all"

    # Marker filtresi
    marker_filtre = None
    if kategori in ("smoke", "unit", "cua"):
        marker_filtre = kategori
    elif kategori.startswith("marker:"):
        marker_filtre = kategori.split(":", 1)[1]
        kategori = "marker"

    if marker_filtre:
        print(
            f"  {renkli(f'Marker filtresi: {marker_filtre}', 'mavi')}"
        )

    if args.watch:
        print(f"{renkli('Watch modu aktif...', 'sari')}")
        try:
            import watchdog.events
            import watchdog.observers

            class TestCalistirici(watchdog.events.PatternMatchingEventHandler):
                def on_modified(self, event):
                    if event.src_path.endswith(".py"):
                        print(
                            f"\n{renkli('[Degisiklik algilandi]', 'sari')} "
                            f"{os.path.basename(event.src_path)}"
                        )
                        ana_calistir(kategori, args.html, args.json, args.cron)

            observer = watchdog.observers.Observer()
            handler = TestCalistirici(patterns=["*.py"])
            observer.schedule(handler, str(ROOT), recursive=True)
            observer.start()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                observer.stop()
            observer.join()
        except ImportError:
            print(
                f"{renkli('watchdog modulu gerekli: pip install watchdog', 'sari')}"
            )
            return 1
    else:
        sonuc = ana_calistir(kategori, args.html, args.json, args.cron, marker_filtre)
        return 0 if sonuc.get("genel_durum", False) else 1


if __name__ == "__main__":
    sys.exit(main())
