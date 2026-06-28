# -*- coding: utf-8 -*-
"""cron/suggestion_catalog.py — Oneri Katalogu.

Onceden tanimlanmis cron is onerileri katalogu. Her kayit bir
``CatalogEntry`` orneginden olusur. ``seed_catalog_suggestions`` fonksiyonu
bu kayitlari oneri deposuna ekler.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CatalogEntry:
    """Katalogdaki tek bir oneri girisi."""
    key: str
    title: str
    description: str
    job_spec: dict = field(default_factory=dict)


def classify_items_script_path() -> str:
    """classify_items.py betik dosyasinin mutlak yolunu dondur.

    NOT: Bu fonksiyon sadece betik dosyasinin varligini dogrulamak icindir.
    Cron is tanımlarinda asla mutlak yol kullanma; her zaman
    ``cron.scripts.classify_items`` modul yolunu kullan.
    """
    return str(Path(__file__).parent / "scripts" / "classify_items.py")


CATALOG: list = [
    CatalogEntry(
        key="catalog:important-mail-monitor",
        title="Important Mail Monitor",
        description=(
            "Her saat gelen kutusu taranir; onemli e-postalar siniflandirilir ve iletilir."
        ),
        job_spec={
            "name": "Important Mail Monitor",
            "prompt": (
                "Check the inbox and use cron.scripts.classify_items to identify "
                "important messages. Deliver a summary of any high-priority items."
            ),
            "schedule": "0 * * * *",
            "deliver": "origin",
            "skills": [],
        },
    ),
    CatalogEntry(
        key="catalog:daily-summary",
        title="Daily Summary",
        description="Her sabah 08:00'de gunluk ozet rapor olusturur.",
        job_spec={
            "name": "Daily Summary",
            "prompt": "Generate a concise daily summary of tasks, events and updates.",
            "schedule": "0 8 * * *",
            "deliver": "origin",
            "skills": [],
        },
    ),
    CatalogEntry(
        key="catalog:weekly-review",
        title="Weekly Review",
        description="Her Pazartesi 09:00'da haftalik degerlendirme raporu olusturur.",
        job_spec={
            "name": "Weekly Review",
            "prompt": "Create a weekly review covering completed tasks and upcoming priorities.",
            "schedule": "0 9 * * 1",
            "deliver": "origin",
            "skills": [],
        },
    ),
]


def seed_catalog_suggestions(add_fn=None) -> list:
    """Katalog girislerini oneri deposuna ekle.

    Args:
        add_fn: ``cron.suggestions.add_suggestion`` benzeri callable.
                None ise modulu direkt import eder.

    Returns:
        Basarili sekilde eklenen oneri kayitlari listesi (None'lar dahil degil).
    """
    if add_fn is None:
        import cron.suggestions as _s
        add_fn = _s.add_suggestion

    created = []
    for entry in CATALOG:
        rec = add_fn(
            title=entry.title,
            description=entry.description,
            source="catalog",
            job_spec=entry.job_spec,
            dedup_key=entry.key,
        )
        if rec is not None:
            created.append(rec)
    return created


if __name__ == "__main__":
    print("Katalog girisi sayisi:", len(CATALOG))
    print("classify_items_script_path():", classify_items_script_path())
    for entry in CATALOG:
        print(f"  - {entry.key}: {entry.title}")
