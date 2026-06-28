"""📊 Kanban geliştirme — Kart, kolon, öncelik, deadline.

Görevleri kanban panosunda yönetir. Kartlar kolonlar arasında taşınabilir,
önceliklendirilebilir ve deadline takibi yapılabilir. Veriler JSON olarak
saklanır.

Örnek::

    from ReYMeN.kanban import Board, Card, Priority

    board = Board.load("board.json")
    card = Card(title="Özellik ekle", priority=Priority.HIGH)
    board.add(card, "todo")
    board.move(card.id, "doing")
    board.save()
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import IntEnum
from pathlib import Path
from typing import Any

__all__ = [
    "Priority",
    "Card",
    "Column",
    "Board",
]


# ---------------------------------------------------------------------------
# Priority
# ---------------------------------------------------------------------------
class Priority(IntEnum):
    """Kart öncelik seviyeleri (düşük sayı = yüksek öncelik)."""

    CRITICAL = 0
    HIGH = 1
    MEDIUM = 2
    LOW = 3
    BACKLOG = 4

    @classmethod
    def from_str(cls, value: str | int | "Priority") -> "Priority":
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        s = str(value).strip().upper()
        # İsim veya değer ile eşleştir
        for p in cls:
            if p.name == s or str(p.value) == s:
                return p
        # Yaygın alias'lar
        aliases = {
            "URGENT": cls.CRITICAL,
            "BLOCKER": cls.CRITICAL,
            "NORMAL": cls.MEDIUM,
            "TRIVIAL": cls.LOW,
        }
        if s in aliases:
            return aliases[s]
        raise ValueError(f"Geçersiz öncelik: {value!r}")

    def __str__(self) -> str:
        return self.name


# ---------------------------------------------------------------------------
# Card
# ---------------------------------------------------------------------------
@dataclass
class Card:
    """Kanban kartı."""

    title: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    description: str = ""
    priority: Priority = Priority.MEDIUM
    deadline: str | None = None  # ISO 8601 tarih
    tags: list[str] = field(default_factory=list)
    assignee: str | None = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    order: int = 0

    def touch(self) -> None:
        """``updated_at`` alanını günceller."""
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def is_overdue(self, now: str | None = None) -> bool:
        """Deadline geçmiş mi?"""
        if not self.deadline:
            return False
        now = now or datetime.now(timezone.utc).isoformat()
        return self.deadline < now

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["priority"] = int(self.priority)
        d["priority_name"] = self.priority.name
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Card":
        data = dict(data)
        if "priority" in data:
            data["priority"] = Priority.from_str(data["priority"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Column
# ---------------------------------------------------------------------------
@dataclass
class Column:
    """Kanban kolonu (kart listesi)."""

    name: str
    cards: list[Card] = field(default_factory=list)
    wip_limit: int | None = None  # Work-in-progress limiti

    def add(self, card: Card) -> None:
        """Kart ekler (WIP limiti kontrolü ile)."""
        if self.wip_limit is not None and len(self.cards) >= self.wip_limit:
            raise ValueError(
                f"Kolon '{self.name}' WIP limitine ({self.wip_limit}) ulaştı"
            )
        card.order = len(self.cards)
        self.cards.append(card)

    def remove(self, card_id: str) -> Card | None:
        """Kartı çıkarır ve döndürür."""
        for i, c in enumerate(self.cards):
            if c.id == card_id:
                return self.cards.pop(i)
        return None

    def get(self, card_id: str) -> Card | None:
        """Kartı bulur."""
        for c in self.cards:
            if c.id == card_id:
                return c
        return None

    def sort_by_priority(self) -> None:
        """Kartları önceliğe göre sıralar."""
        self.cards.sort(key=lambda c: (c.priority, c.order))
        for i, c in enumerate(self.cards):
            c.order = i

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "wip_limit": self.wip_limit,
            "cards": [c.as_dict() for c in self.cards],
        }


# ---------------------------------------------------------------------------
# Board
# ---------------------------------------------------------------------------
class Board:
    """Kanban panosu.

    Varsayılan kolonlar: ``todo``, ``doing``, ``done``.
    """

    DEFAULT_COLUMNS = ["todo", "doing", "done"]

    def __init__(
        self,
        name: str = "Pano",
        columns: list[Column] | None = None,
    ) -> None:
        self.name = name
        if columns is None:
            self.columns: list[Column] = [
                Column(name=n) for n in self.DEFAULT_COLUMNS
            ]
        else:
            self.columns = columns

    # -- Kolon işlemleri ----------------------------------------------------
    def add_column(self, name: str, wip_limit: int | None = None) -> Column:
        """Yeni kolon ekler."""
        if self.get_column(name):
            raise ValueError(f"Kolon '{name}' zaten var")
        col = Column(name=name, wip_limit=wip_limit)
        self.columns.append(col)
        return col

    def get_column(self, name: str) -> Column | None:
        for col in self.columns:
            if col.name == name:
                return col
        return None

    def remove_column(self, name: str) -> bool:
        col = self.get_column(name)
        if col is None:
            return False
        self.columns.remove(col)
        return True

    # -- Kart işlemleri -----------------------------------------------------
    def add(
        self,
        card: Card,
        column: str = "todo",
    ) -> Card:
        """Kartı belirtilen kolona ekler."""
        col = self.get_column(column)
        if col is None:
            raise ValueError(f"Kolon '{column}' bulunamadı")
        col.add(card)
        return card

    def move(self, card_id: str, to_column: str) -> Card:
        """Kartı başka bir kolona taşır."""
        target = self.get_column(to_column)
        if target is None:
            raise ValueError(f"Hedef kolon '{to_column}' bulunamadı")
        # Kaynak kolonu bul
        for col in self.columns:
            card = col.get(card_id)
            if card is not None:
                col.remove(card_id)
                card.touch()
                target.add(card)
                return card
        raise ValueError(f"Kart '{card_id}' bulunamadı")

    def prioritize(self, card_id: str, priority: Priority | str) -> Card:
        """Kartın önceliğini günceller."""
        priority = Priority.from_str(priority)
        for col in self.columns:
            card = col.get(card_id)
            if card is not None:
                card.priority = priority
                card.touch()
                col.sort_by_priority()
                return card
        raise ValueError(f"Kart '{card_id}' bulunamadı")

    def set_deadline(self, card_id: str, deadline: str) -> Card:
        """Kartın deadline'ını ayarlar (ISO 8601)."""
        for col in self.columns:
            card = col.get(card_id)
            if card is not None:
                card.deadline = deadline
                card.touch()
                return card
        raise ValueError(f"Kart '{card_id}' bulunamadı")

    def find(self, card_id: str) -> Card | None:
        """Kartı tüm kolonlarda arar."""
        for col in self.columns:
            card = col.get(card_id)
            if card is not None:
                return card
        return None

    def all_cards(self) -> list[Card]:
        """Tüm kartları döndürür."""
        return [c for col in self.columns for c in col.cards]

    def overdue_cards(self) -> list[Card]:
        """Deadline'ı geçmiş kartları döndürür."""
        return [c for c in self.all_cards() if c.is_overdue()]

    # -- Özet ---------------------------------------------------------------
    def summary(self) -> dict[str, Any]:
        """Pano özeti."""
        return {
            "name": self.name,
            "columns": {
                col.name: {
                    "count": len(col.cards),
                    "wip_limit": col.wip_limit,
                    "over_limit": (
                        col.wip_limit is not None
                        and len(col.cards) > col.wip_limit
                    ),
                }
                for col in self.columns
            },
            "total_cards": len(self.all_cards()),
            "overdue": len(self.overdue_cards()),
        }

    # -- Serileştirme -------------------------------------------------------
    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "columns": [col.as_dict() for col in self.columns],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.as_dict(), indent=indent, ensure_ascii=False)

    def save(self, path: str | Path) -> None:
        """Panoyu JSON dosyasına kaydeder."""
        Path(path).write_text(self.to_json(), encoding="utf-8")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Board":
        columns = [
            Column(
                name=c["name"],
                wip_limit=c.get("wip_limit"),
                cards=[Card.from_dict(card) for card in c.get("cards", [])],
            )
            for c in data.get("columns", [])
        ]
        return cls(name=data.get("name", "Pano"), columns=columns)

    @classmethod
    def load(cls, path: str | Path) -> "Board":
        """JSON dosyasından pano yükler."""
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls.from_dict(data)