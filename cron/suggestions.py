# -*- coding: utf-8 -*-
"""cron/suggestions.py — Otomatik Gorev Oneri Deposu.

Bekleyen, kabul edilmis ve reddedilen cron is onerileri.
Veriler ~/.ReYMeN/cron/suggestions.json dosyasinda saklanir.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

MAX_PENDING = 20
VALID_SOURCES = frozenset({"catalog", "blueprint"})


def _suggestions_file() -> Path:
    """Oneri depo dosyasi yolunu dondur."""
    try:
        import ReYMeN_constants
        home = Path(ReYMeN_constants.get_ReYMeN_home())
    except Exception:
        home = Path.home() / ".ReYMeN"
    return home / "cron" / "suggestions.json"


def _load() -> list:
    """Oneri deposunu diskten yukle."""
    f = _suggestions_file()
    if not f.exists():
        return []
    try:
        with open(str(f), "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if isinstance(data, list):
                return data
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")
    return []


def _save(records: list) -> None:
    """Oneri deposunu diske kaydet."""
    f = _suggestions_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    with open(str(f), "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=2)


def add_suggestion(*, title: str, description: str, source: str, job_spec: dict, dedup_key: str):
    """Oneri ekle. Zaten varsa None dondur.

    Args:
        title: Oneri basligi
        description: Oneri aciklamasi
        source: Oneri kaynagi ("catalog" veya "blueprint")
        job_spec: Is tanimlamasi
        dedup_key: Tekrar kontrol anahtari

    Returns:
        Yeni oneri kaydi veya None (zaten var veya kapasite asimi)

    Raises:
        ValueError: Gecersiz kaynak
    """
    if source not in VALID_SOURCES:
        raise ValueError(
            f"Invalid source {source!r}; must be one of {sorted(VALID_SOURCES)}"
        )

    records = _load()

    # Dedup check across ALL statuses.
    for r in records:
        if r.get("dedup_key") == dedup_key:
            return None

    # Cap pending count.
    pending_count = sum(1 for r in records if r.get("status") == "pending")
    if pending_count >= MAX_PENDING:
        return None

    rec = {
        "id": str(uuid.uuid4()),
        "title": title,
        "description": description,
        "source": source,
        "job_spec": job_spec,
        "dedup_key": dedup_key,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    records.append(rec)
    _save(records)
    return rec


def list_pending() -> list:
    """Bekleyen onerileri dondur."""
    return [r for r in _load() if r.get("status") == "pending"]


def get_suggestion(ref: str):
    """Referansa gore oneri bul.

    Ref sirasini dener: kesin ID → 1-tabanli bekleyen indeksi → baslik.

    Returns:
        Oneri kaydi veya None
    """
    if not ref:
        return None

    records = _load()

    # 1. Exact ID match (any status).
    for r in records:
        if r.get("id") == ref:
            return r

    # 2. 1-based pending index.
    try:
        idx = int(ref)
        pending = [r for r in records if r.get("status") == "pending"]
        if 1 <= idx <= len(pending):
            return pending[idx - 1]
    except (ValueError, TypeError):
        logger.warning("[fix_01_sessiz_except] Exception")

    # 3. Case-insensitive title match (all statuses).
    ref_lower = ref.lower()
    for r in records:
        if r.get("title", "").lower() == ref_lower:
            return r

    return None


def dismiss_suggestion(ref: str) -> bool:
    """Oneriyi reddet; latch icin kaydi sakla (asla yeniden gosterme).

    Returns:
        True if found and dismissed, False otherwise.
    """
    rec = get_suggestion(ref)
    if rec is None or rec.get("status") != "pending":
        return False

    records = _load()
    for r in records:
        if r["id"] == rec["id"]:
            r["status"] = "dismissed"
            r["dismissed_at"] = datetime.now(timezone.utc).isoformat()
            break
    _save(records)
    return True


def accept_suggestion(ref: str, origin=None):
    """Oneriyi kabul et ve cron is olustur.

    Args:
        ref: Oneri referansi (ID, indeks veya baslik)
        origin: Is kaynagi bilgisi (platform, chat_id vb.)

    Returns:
        Olusturulan is kaydi veya None
    """
    rec = get_suggestion(ref)
    if rec is None or rec.get("status") != "pending":
        return None

    import cron.jobs as jobs

    job_spec = dict(rec.get("job_spec", {}))
    if origin is not None:
        job_spec["origin"] = origin

    job = jobs.create_job(**job_spec)

    records = _load()
    for r in records:
        if r["id"] == rec["id"]:
            r["status"] = "accepted"
            r["accepted_at"] = datetime.now(timezone.utc).isoformat()
            break
    _save(records)
    return job


def clear_resolved() -> int:
    """Kabul edilmis onerileri kaldir. Reddedilenleri sakla (latch icin).

    Returns:
        Kaldirilan kayit sayisi
    """
    records = _load()
    before = len(records)
    records = [r for r in records if r.get("status") != "accepted"]
    _save(records)
    return before - len(records)


if __name__ == "__main__":
    print("MAX_PENDING:", MAX_PENDING)
    print("VALID_SOURCES:", VALID_SOURCES)
    print("Suggestions file:", _suggestions_file())
    print("list_pending():", list_pending())
