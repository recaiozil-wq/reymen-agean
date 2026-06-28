# -*- coding: utf-8 -*-
"""tests/website/scripts/extract-automation-blueprints.py

ReYMeN referans testleri icin kopya: tests/ReYMeN_reference/cron/test_blueprint_catalog.py
parents[2] / "website" / "scripts" konumuna bakar, bu dosyayi bulur.
Gercek ureticiye delege eder.
"""

from __future__ import annotations


def build_index() -> list:
    """Katalogdaki tum blueprint'lerin JSON-seri-uyumlu listesini dondur."""
    from cron.blueprint_catalog import CATALOG, blueprint_catalog_entry

    return [blueprint_catalog_entry(entry) for entry in CATALOG]
