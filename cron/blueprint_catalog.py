# -*- coding: utf-8 -*-
"""cron/blueprint_catalog.py — Otomasyon Blueprint Katalogu.

Parametreli otomasyon sablonlari (blueprint) sistemi.
Her blueprint; doldurulabilir slot'lara, bir zamanlama sablonuna ve
bir prompt sablonuna sahiptir. fill_blueprint() ile somut is tanımına donusur.
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from urllib.parse import urlencode

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BlueprintFillError(Exception):
    """Blueprint slot doldurma hatasi."""


# ---------------------------------------------------------------------------
# Slot types
# ---------------------------------------------------------------------------

KNOWN_SLOT_TYPES = frozenset({"time", "enum", "text", "weekdays"})


@dataclass
class BlueprintSlot:
    """Bir blueprint slot tanimlayicisi."""

    name: str
    type: str
    label: str
    default: str = ""
    options: List[str] = field(default_factory=list)
    strict: bool = True  # enum: sadece listelenen degerler gecerli

    def __post_init__(self):
        if self.type not in KNOWN_SLOT_TYPES:
            raise ValueError(
                f"Unknown slot type {self.type!r}; must be one of {sorted(KNOWN_SLOT_TYPES)}"
            )


# ---------------------------------------------------------------------------
# Blueprint entry
# ---------------------------------------------------------------------------


@dataclass
class BlueprintEntry:
    """Tek bir otomasyon blueprint'i."""

    key: str
    title: str
    description: str
    prompt_template: str
    slots: List[BlueprintSlot]
    schedule_template: str
    deliver_default: str = "origin"


# ---------------------------------------------------------------------------
# Day → DOW mapping
# ---------------------------------------------------------------------------

_DAY_TO_DOW = {
    "sunday": 0, "monday": 1, "tuesday": 2, "wednesday": 3,
    "thursday": 4, "friday": 5, "saturday": 6,
}

# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------

CATALOG: List[BlueprintEntry] = [
    BlueprintEntry(
        key="morning-brief",
        title="Morning Brief",
        description="Get a daily summary at a time you choose.",
        prompt_template=(
            "Create a morning brief: summarize today's schedule, "
            "news highlights, and any urgent items."
        ),
        slots=[
            BlueprintSlot(name="time", type="time", label="Time", default="08:00"),
            BlueprintSlot(
                name="deliver", type="enum", label="Deliver to", default="origin",
                options=["origin", "telegram", "slack", "email"], strict=False,
            ),
        ],
        schedule_template="TIME",
    ),
    BlueprintEntry(
        key="important-mail",
        title="Important Mail Monitor",
        description="Check your inbox on an interval and alert you about important messages.",
        prompt_template=(
            "Check the inbox every {interval_min} minutes. "
            "Look for messages matching: {criteria}. Summarize and deliver urgent ones."
        ),
        slots=[
            BlueprintSlot(
                name="interval_min", type="enum", label="Check every (minutes)", default="15",
                options=["5", "10", "15", "30", "60"], strict=True,
            ),
            BlueprintSlot(
                name="criteria", type="text", label="What counts as important?",
                default="urgent messages",
            ),
            BlueprintSlot(
                name="deliver", type="enum", label="Deliver to", default="origin",
                options=["origin", "telegram", "slack", "email"], strict=False,
            ),
        ],
        schedule_template="INTERVAL_MIN",
    ),
    BlueprintEntry(
        key="weekly-review",
        title="Weekly Review",
        description="A weekly recap and planning session on the day and time you pick.",
        prompt_template=(
            "Create a weekly review: summarize completed tasks, "
            "upcoming priorities, and suggest improvements."
        ),
        slots=[
            BlueprintSlot(name="time", type="time", label="Time", default="09:00"),
            BlueprintSlot(
                name="day", type="enum", label="Day of week", default="monday",
                options=[
                    "sunday", "monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday",
                ], strict=True,
            ),
            BlueprintSlot(
                name="deliver", type="enum", label="Deliver to", default="origin",
                options=["origin", "telegram", "slack", "email"], strict=False,
            ),
        ],
        schedule_template="DOW",
    ),
    BlueprintEntry(
        key="custom-reminder",
        title="Custom Reminder",
        description="A recurring reminder for anything you choose.",
        prompt_template="Remind me to {what}. Send a brief motivating message.",
        slots=[
            BlueprintSlot(
                name="what", type="text", label="What to remind you about?", default="check in",
            ),
            BlueprintSlot(name="time", type="time", label="Time", default="09:00"),
            BlueprintSlot(
                name="recurrence", type="weekdays", label="How often?", default="weekdays",
                options=[
                    "daily", "weekdays", "weekends",
                    "monday", "tuesday", "wednesday", "thursday",
                    "friday", "saturday", "sunday",
                ], strict=True,
            ),
            BlueprintSlot(
                name="deliver", type="enum", label="Deliver to", default="origin",
                options=["origin", "telegram", "slack", "email"], strict=False,
            ),
        ],
        schedule_template="RECURRENCE",
    ),
    BlueprintEntry(
        key="news-digest",
        title="News Digest",
        description="A curated news digest delivered daily.",
        prompt_template=(
            "Fetch and summarize the top {count} news stories. "
            "Focus on technology and world events."
        ),
        slots=[
            BlueprintSlot(
                name="count", type="enum", label="Number of stories", default="5",
                options=["5", "10", "15", "25"], strict=True,
            ),
            BlueprintSlot(
                name="deliver", type="enum", label="Deliver to", default="origin",
                options=["origin", "telegram", "slack", "email"], strict=False,
            ),
        ],
        schedule_template="0 8 * * *",
    ),
    BlueprintEntry(
        key="hydration-move",
        title="Hydration & Movement Reminder",
        description="Regular reminders to drink water and stretch throughout the day.",
        prompt_template=(
            "Time to hydrate and move! Send an encouraging reminder "
            "to drink water and do a 5-minute stretch."
        ),
        slots=[
            BlueprintSlot(
                name="interval_hours", type="enum", label="Remind every (hours)", default="2",
                options=["1", "2", "3", "4", "6"], strict=True,
            ),
        ],
        schedule_template="INTERVAL_HOURS",
    ),
]

# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------


def get_blueprint(key: str) -> Optional[BlueprintEntry]:
    """Anahtarla blueprint bul. Bulunamazsa None dondur."""
    for entry in CATALOG:
        if entry.key == key:
            return entry
    return None


# ---------------------------------------------------------------------------
# Time parsing
# ---------------------------------------------------------------------------


def _parse_time(value: str):
    """'HH:MM' → (hour, minute). Hatali giris icin BlueprintFillError."""
    match = re.fullmatch(r"(\d{1,2}):(\d{2})", (value or "").strip())
    if not match:
        raise BlueprintFillError(f"invalid time {value!r}: must be HH:MM (00:00–23:59)")
    h, m = int(match.group(1)), int(match.group(2))
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise BlueprintFillError(f"invalid time {value!r}: hours 0-23, minutes 0-59")
    return h, m


# ---------------------------------------------------------------------------
# Schedule resolution
# ---------------------------------------------------------------------------


def _resolve_schedule(entry: BlueprintEntry, filled: dict) -> str:
    tmpl = entry.schedule_template

    if tmpl == "TIME":
        h, m = _parse_time(filled.get("time", "08:00"))
        return f"{m} {h} * * *"

    if tmpl == "INTERVAL_MIN":
        n = filled.get("interval_min", "15")
        return f"*/{n} * * * *"

    if tmpl == "DOW":
        h, m = _parse_time(filled.get("time", "09:00"))
        day = (filled.get("day") or "monday").lower()
        dow = _DAY_TO_DOW.get(day, 1)
        return f"{m} {h} * * {dow}"

    if tmpl == "RECURRENCE":
        h, m = _parse_time(filled.get("time", "09:00"))
        rec = (filled.get("recurrence") or "weekdays").lower()
        dow_map = {"daily": "*", "weekdays": "1-5", "weekends": "0,6"}
        if rec in dow_map:
            dow = dow_map[rec]
        elif rec in _DAY_TO_DOW:
            dow = str(_DAY_TO_DOW[rec])
        else:
            dow = "*"
        return f"{m} {h} * * {dow}"

    if tmpl == "INTERVAL_HOURS":
        n = filled.get("interval_hours", "2")
        return f"0 */{n} * * *"

    return tmpl


def _schedule_human(entry: BlueprintEntry) -> str:
    """Insan okunakli zamanlama aciklamasi."""
    tmpl = entry.schedule_template
    default_time = next((s.default for s in entry.slots if s.name == "time"), "08:00")
    if tmpl == "TIME":
        return f"Daily at {default_time}"
    if tmpl == "INTERVAL_MIN":
        n = next((s.default for s in entry.slots if s.name == "interval_min"), "15")
        return f"Every {n} minutes"
    if tmpl == "DOW":
        day = next((s.default for s in entry.slots if s.name == "day"), "monday")
        return f"Every {day.capitalize()} at {default_time}"
    if tmpl == "RECURRENCE":
        return "On a custom schedule"
    if tmpl == "INTERVAL_HOURS":
        n = next((s.default for s in entry.slots if s.name == "interval_hours"), "2")
        return f"Every {n} hours"
    return "Scheduled"


# ---------------------------------------------------------------------------
# fill_blueprint
# ---------------------------------------------------------------------------


def fill_blueprint(entry: BlueprintEntry, user_slots: dict, origin: dict = None) -> dict:
    """Blueprint slot'larini doldur ve is tanimlama sozlugu dondur.

    Args:
        entry: Blueprint girisi
        user_slots: Kullanicidan gelen slot degerleri
        origin: Is kaynagi (platform, chat_id vb.)

    Returns:
        Cron is tanimlama sozlugu

    Raises:
        BlueprintFillError: Gecersiz slot degeri veya bilinmeyen slot adi
    """
    slot_names = {s.name for s in entry.slots}

    # Bilinmeyen slot adlari reddet.
    for key in user_slots:
        if key not in slot_names:
            raise BlueprintFillError(
                f"unknown slot {key!r} for blueprint {entry.key!r}"
            )

    # Varsayilanlarla birlestir ve dogrula.
    filled: Dict[str, str] = {}
    for slot in entry.slots:
        val = user_slots.get(slot.name, slot.default)

        if slot.type == "time":
            _parse_time(val)  # validation only

        elif slot.type == "enum" and slot.strict and slot.options:
            if val not in slot.options:
                raise BlueprintFillError(
                    f"{val!r} not allowed for slot {slot.name!r}; "
                    f"valid options: {slot.options}"
                )

        filled[slot.name] = val

    schedule = _resolve_schedule(entry, filled)

    # Prompt sablonuna slot degerlerini yerlestir.
    prompt = entry.prompt_template
    for k, v in filled.items():
        prompt = prompt.replace("{" + k + "}", v)

    spec: Dict[str, Any] = {
        "name": entry.title,
        "schedule": schedule,
        "schedule_display": schedule,
        "prompt": prompt,
        "deliver": filled.get("deliver", entry.deliver_default),
    }
    if origin is not None:
        spec["origin"] = origin
    return spec


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------


def blueprint_form_schema(entry: BlueprintEntry) -> dict:
    """Blueprint icin form sema sozlugu dondur."""
    fields = []
    for slot in entry.slots:
        f: Dict[str, Any] = {
            "name": slot.name,
            "type": slot.type,
            "label": slot.label,
            "default": slot.default,
        }
        if slot.options:
            f["options"] = slot.options
        fields.append(f)
    return {"key": entry.key, "fields": fields}


def blueprint_slash_command(entry: BlueprintEntry, user_slots: dict = None) -> str:
    """Blueprint icin `/blueprint key slot=value ...` dizesi uret."""
    parts = [f"/blueprint {entry.key}"]
    for slot in entry.slots:
        val = (user_slots or {}).get(slot.name, slot.default)
        if slot.type == "text" and " " in str(val):
            parts.append(f'{slot.name}="{val}"')
        else:
            parts.append(f"{slot.name}={val}")
    return " ".join(parts)


def blueprint_deeplink(entry: BlueprintEntry, user_slots: dict = None) -> str:
    """Blueprint icin ReYMeN:// derin baglantiyi uret."""
    params = {}
    for slot in entry.slots:
        params[slot.name] = (user_slots or {}).get(slot.name, slot.default)
    return f"ReYMeN://blueprint/{entry.key}?{urlencode(params)}"


def blueprint_catalog_entry(entry: BlueprintEntry) -> dict:
    """Bir blueprint'in tum yuzeyleri iceren sozlugunu dondur."""
    return {
        "key": entry.key,
        "title": entry.title,
        "description": entry.description,
        "command": blueprint_slash_command(entry),
        "appUrl": blueprint_deeplink(entry),
        "scheduleHuman": _schedule_human(entry),
        "fields": blueprint_form_schema(entry)["fields"],
    }


if __name__ == "__main__":
    print(f"Blueprint katalogu: {len(CATALOG)} giris")
    for entry in CATALOG:
        print(f"  - {entry.key}: {entry.title}")
