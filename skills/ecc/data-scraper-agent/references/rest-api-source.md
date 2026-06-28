---
skill_id: 01046b353aac
usage_count: 1
last_used: 2026-06-16
---
# ---- REST API source ----
    resp = requests.get("https://api.example.com/items", headers=HEADERS, timeout=15)
    if resp.status_code == 200:
        for item in resp.json().get("results", []):
            if not is_relevant(item.get("title", "")):
                continue
            results.append(_normalise(item))

    return results


def _normalise(raw: dict) -> dict:
    """Convert raw API/HTML data to the standard schema."""
    return {
        "name": raw.get("title", ""),
        "url": raw.get("link", ""),
        "source": "MySource",
        "date_found": datetime.now(timezone.utc).date().isoformat(),