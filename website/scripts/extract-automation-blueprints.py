#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""website/scripts/extract-automation-blueprints.py — Otomasyon Blueprint Dizini Uretici.

Bu betik cron/blueprint_catalog.py'deki CATALOG'u okuyarak web sitesi icin
JSON dizini (blueprint_index.json) uretir.

Kullanim:
    python website/scripts/extract-automation-blueprints.py
    python website/scripts/extract-automation-blueprints.py --out dist/blueprint_index.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Proje koku sys.path'a ekle (dogrudan calistirma icin)
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def build_index() -> list:
    """Katalogdaki tum blueprint'lerin JSON-seri-uyumlu listesini dondur."""
    from cron.blueprint_catalog import CATALOG, blueprint_catalog_entry

    return [blueprint_catalog_entry(entry) for entry in CATALOG]


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Otomasyon blueprint katalogunu JSON dizinine donustur"
    )
    parser.add_argument(
        "--out",
        default=str(_PROJECT_ROOT / "website" / "dist" / "blueprint_index.json"),
        help="Cikti dosya yolu",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        default=True,
        help="Girdili (pretty-print) JSON cikti",
    )
    args = parser.parse_args()

    index = build_index()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    indent = 2 if args.pretty else None
    with open(str(out_path), "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=indent)

    print(f"[blueprint-index] {len(index)} girdi yazildi: {out_path}")


if __name__ == "__main__":
    main()
