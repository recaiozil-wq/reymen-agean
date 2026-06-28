#!/usr/bin/env python3
"""
auto_xai_fix.py
Klasor yolunu elle yazmana, cd yapmana GEREK YOK.
Bu script kendi basina:
  1) Bilgisayarinda xai_http.py dosyasini arar (sen sadece calistirirsin)
  2) Proje kokunu otomatik tespit eder
  3) hermes_xai_user_agent sorununu tanir
  4) Sorun varsa otomatik duzeltir (yedek alarak, hicbir seyi silmeden)
  5) Rapor dosyasi yazar

Kullanim (baska hicbir sey yazmadan, oldugun yerde calistir):
    python auto_xai_fix.py

Sadece tani koysun, dosyaya dokunmasin istersen:
    python auto_xai_fix.py --no-fix

Aramanin ev dizini disinda baska bir yerden baslamasini istersen:
    python auto_xai_fix.py --search "D:\\"
"""

import argparse
import ast
import datetime
import os
import sys
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except AttributeError:
    logger.warning("[fix_01_sessiz_except] AttributeError")

TARGET_SYMBOL = "hermes_xai_user_agent"
XAI_FILE_NAME = "xai_http.py"
SKIP_DIRS = {
    "AppData", "$Recycle.Bin", "Windows", "ProgramData", "node_modules",
    "venv", ".venv", "__pycache__", ".git", "Cache", "Caches",
}


def find_xai_candidates(start: Path):
    """os.walk ile start altindaki tum xai_http.py dosyalarini bulur (gurultulu klasorleri atlar)."""
    found = []
    for dirpath, dirnames, filenames in os.walk(start, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        if XAI_FILE_NAME in filenames:
            p = Path(dirpath) / XAI_FILE_NAME
            try:
                mtime = p.stat().st_mtime
            except OSError:
                mtime = 0
            found.append((p, mtime))
    return found


def pick_best_candidate(candidates):
    """Birden fazla bulunursa en son degistirileni 'aktif proje' say."""
    return max(candidates, key=lambda c: c[1])[0]


def detect_project_root(xai_path: Path):
    """xai_http.py 'tools' klasoru altindaysa proje kokunu (tools'un bir ustu) verir."""
    if xai_path.parent.name.lower() == "tools":
        return xai_path.parent.parent
    return xai_path.parent


def search_symbol(root: Path, symbol: str):
    definitions, usages = [], []
    for path in root.rglob("*.py"):
        if SKIP_DIRS & set(path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if symbol not in line:
                continue
            stripped = line.strip()
            rel = path.relative_to(root)
            is_def = stripped.startswith(("def " + symbol, "class " + symbol))
            is_assign = stripped.startswith(symbol + " =") or stripped.startswith(symbol + "=")
            (definitions if (is_def or is_assign) else usages).append((rel, lineno, stripped))
    return definitions, usages


def get_top_level_defs(file_path: Path):
    names = []
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.append(("def", node.name, node.lineno))
            elif isinstance(node, ast.ClassDef):
                names.append(("class", node.name, node.lineno))
            elif isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        names.append(("var", t.id, node.lineno))
    except SyntaxError as e:
        names.append(("ERROR", f"SyntaxError: {e}", 0))
    return names


def build_report(root, definitions, usages, xai_path, xai_defs):
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    L = [
        "# xai Plugin Tani Raporu (otomatik)",
        f"Tarih: {now}",
        f"Tespit edilen proje: {root}",
        f"Bulunan dosya: {xai_path}",
        "",
        f"## Hedef sembol: `{TARGET_SYMBOL}`",
        "",
        f"### Tanimlar ({len(definitions)})",
    ]
    L += [f"- `{r}:{n}` -> `{c}`" for r, n, c in definitions] or ["- YOK"]
    L.append(f"\n### Kullanimlar/Importlar ({len(usages)})")
    L += [f"- `{r}:{n}` -> `{c}`" for r, n, c in usages] or ["- YOK"]
    L.append(f"\n## {xai_path.name} icinde tanimli isimler")
    L += [f"- [{k}] `{n}` (satir {ln})" for k, n, ln in xai_defs] or ["- YOK"]
    return "\n".join(L)


def apply_fix(xai_path: Path, xai_defs):
    func_names = [n for k, n, _ in xai_defs if k == "def"]
    if not func_names:
        return None
    text = xai_path.read_text(encoding="utf-8", errors="replace")
    if TARGET_SYMBOL in text:
        return "ALREADY_PRESENT"
    backup = xai_path.with_suffix(xai_path.suffix + ".bak")
    backup.write_text(text, encoding="utf-8")
    new_text = text.rstrip() + (
        f"\n\n# Otomatik eklendi - geriye donuk uyumluluk\n"
        f"{TARGET_SYMBOL} = {func_names[0]}\n"
    )
    xai_path.write_text(new_text, encoding="utf-8")
    return func_names[0]


def main():
    parser = argparse.ArgumentParser(description="xai plugin sorununu otomatik bulup duzeltir")
    parser.add_argument("--search", default=str(Path.home()),
                         help="Aramaya baslanacak klasor (varsayilan: kullanici ev dizini)")
    parser.add_argument("--no-fix", action="store_true", help="Sadece tani koy, dosyaya dokunma")
    args = parser.parse_args()

    start = Path(args.search).resolve()
    print(f"'{XAI_FILE_NAME}' icin taraniyor: {start}")
    print("(Klasor sayisina gore biraz surebilir, bekle...)\n")

    candidates = find_xai_candidates(start)
    if not candidates:
        print(f"HATA: '{XAI_FILE_NAME}' hicbir yerde bulunamadi ({start} altinda).")
        print("Dosya baska bir surucudeyse (orn. D:) --search ile o yolu ver.")
        input("\nKapatmak icin Enter'a bas...")
        sys.exit(1)

    if len(candidates) > 1:
        print(f"UYARI: {len(candidates)} farkli '{XAI_FILE_NAME}' bulundu:")
        for p, mtime in candidates:
            ts = datetime.datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M")
            print(f"  - {p}  (son degisiklik: {ts})")
        print("En son degistirilen otomatik secildi.\n")

    xai_path = pick_best_candidate(candidates)
    project_root = detect_project_root(xai_path)
    print(f"Secilen dosya : {xai_path}")
    print(f"Proje koku    : {project_root}\n")

    definitions, usages = search_symbol(project_root, TARGET_SYMBOL)
    xai_defs = get_top_level_defs(xai_path)

    report = build_report(project_root, definitions, usages, xai_path, xai_defs)
    out_path = project_root / f"xai_tani_raporu_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    out_path.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nRapor kaydedildi: {out_path}\n")

    if args.no_fix:
        print("--no-fix verildi, dosyaya dokunulmadi.")
    elif not definitions and usages:
        result = apply_fix(xai_path, xai_defs)
        if result == "ALREADY_PRESENT":
            print(f"'{TARGET_SYMBOL}' zaten dosyada mevcut, dokunulmadi.")
        elif result:
            print(f"DUZELTME UYGULANDI: '{TARGET_SYMBOL} = {result}' eklendi.")
            print(f"Yedek alindi: {xai_path}.bak")
        else:
            print("Duzeltme uygulanamadi: dosyada fonksiyon tanimi bulunamadi.")
    else:
        print("Bu spesifik hata (tanimsiz sembol) tespit edilmedi, otomatik duzeltme atlandi.")

    input("\nKapatmak icin Enter'a bas...")


if __name__ == "__main__":
    main()
