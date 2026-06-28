"""Kanban birim testleri."""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

import pytest

from ReYMeN.kanban import Board, Card, Column, Priority


class TestPriority:
    def test_from_str_name(self):
        assert Priority.from_str("HIGH") == Priority.HIGH
        assert Priority.from_str("low") == Priority.LOW

    def test_from_str_int(self):
        assert Priority.from_str(0) == Priority.CRITICAL
        assert Priority.from_str(2) == Priority.MEDIUM

    def test_from_str_alias(self):
        assert Priority.from_str("URGENT") == Priority.CRITICAL
        assert Priority.from_str("BLOCKER") == Priority.CRITICAL
        assert Priority.from_str("NORMAL") == Priority.MEDIUM

    def test_from_str_invalid(self):
        with pytest.raises(ValueError):
            Priority.from_str("nonexistent")

    def test_str_representation(self):
        assert str(Priority.HIGH) == "HIGH"

    def test_ordering(self):
        assert Priority.CRITICAL < Priority.HIGH < Priority.MEDIUM < Priority.LOW


class TestCard:
    def test_card_defaults(self):
        card = Card(title="Test")
        assert card.title == "Test"
        assert card.priority == Priority.MEDIUM
        assert card.id  # otomatik ID
        assert card.created_at
        assert card.updated_at

    def test_card_touch_updates_timestamp(self):
        card = Card(title="Test")
        old = card.updated_at
        card.touch()
        assert card.updated_at >= old

    def test_is_overdue_true(self):
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        card = Card(title="Test", deadline=past)
        assert card.is_overdue() is True

    def test_is_overdue_false_future(self):
        future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
        card = Card(title="Test", deadline=future)
        assert card.is_overdue() is False

    def test_is_overdue_no_deadline(self):
        card = Card(title="Test")
        assert card.is_overdue() is False

    def test_as_dict_and_from_dict_roundtrip(self):
        card = Card(title="Test", priority=Priority.HIGH, description="desc")
        d = card.as_dict()
        assert d["priority"] == 1
        assert d["priority_name"] == "HIGH"
        restored = Card.from_dict(d)
        assert restored.title == "Test"
        assert restored.priority == Priority.HIGH
        assert restored.description == "desc"


class TestColumn:
    def test_add_card(self):
        col = Column(name="todo")
        card = Card(title="Task")
        col.add(card)
        assert len(col.cards) == 1
        assert col.cards[0] is card

    def test_wip_limit_exceeded(self):
        col = Column(name="doing", wip_limit=2)
        col.add(Card(title="T1"))
        col.add(Card(title="T2"))
        with pytest.raises(ValueError, match="WIP"):
            col.add(Card(title="T3"))

    def test_remove_card(self):
        col = Column(name="todo")
        card = Card(title="Task")
        col.add(card)
        removed = col.remove(card.id)
        assert removed is card
        assert len(col.cards) == 0

    def test_remove_nonexistent(self):
        col = Column(name="todo")
        assert col.remove("nonexistent") is None

    def test_get_card(self):
        col = Column(name="todo")
        card = Card(title="Task")
        col.add(card)
        assert col.get(card.id) is card
        assert col.get("nope") is None

    def test_sort_by_priority(self):
        col = Column(name="todo")
        col.add(Card(title="Low", priority=Priority.LOW))
        col.add(Card(title="High", priority=Priority.HIGH))
        col.add(Card(title="Critical", priority=Priority.CRITICAL))
        col.sort_by_priority()
        assert col.cards[0].priority == Priority.CRITICAL
        assert col.cards[1].priority == Priority.HIGH
        assert col.cards[2].priority == Priority.LOW


class TestBoard:
    def test_default_columns(self):
        board = Board()
        assert len(board.columns) == 3
        assert board.get_column("todo") is not None
        assert board.get_column("doing") is not None
        assert board.get_column("done") is not None

    def test_add_card(self):
        board = Board()
        card = Card(title="Task")
        board.add(card, "todo")
        assert board.get_column("todo").get(card.id) is card

    def test_add_to_nonexistent_column(self):
        board = Board()
        with pytest.raises(ValueError):
            board.add(Card(title="T"), "nonexistent")

    def test_move_card(self):
        board = Board()
        card = Card(title="Task")
        board.add(card, "todo")
        board.move(card.id, "doing")
        assert board.get_column("todo").get(card.id) is None
        assert board.get_column("doing").get(card.id) is card

    def test_move_nonexistent_card(self):
        board = Board()
        with pytest.raises(ValueError):
            board.move("nonexistent", "doing")

    def test_move_to_nonexistent_column(self):
        board = Board()
        card = Card(title="Task")
        board.add(card, "todo")
        with pytest.raises(ValueError):
            board.move(card.id, "nonexistent")

    def test_prioritize(self):
        board = Board()
        card = Card(title="Task", priority=Priority.LOW)
        board.add(card, "todo")
        board.prioritize(card.id, Priority.CRITICAL)
        assert card.priority == Priority.CRITICAL

    def test_set_deadline(self):
        board = Board()
        card = Card(title="Task")
        board.add(card, "todo")
        board.set_deadline(card.id, "2025-12-31T23:59:59+00:00")
        assert card.deadline == "2025-12-31T23:59:59+00:00"

    def test_find_card(self):
        board = Board()
        card = Card(title="Task")
        board.add(card, "doing")
        assert board.find(card.id) is card
        assert board.find("nope") is None

    def test_all_cards(self):
        board = Board()
        board.add(Card(title="T1"), "todo")
        board.add(Card(title="T2"), "doing")
        board.add(Card(title="T3"), "done")
        assert len(board.all_cards()) == 3

    def test_overdue_cards(self):
        board = Board()
        past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        board.add(Card(title="Overdue", deadline=past), "todo")
        board.add(Card(title="Normal"), "todo")
        overdue = board.overdue_cards()
        assert len(overdue) == 1
        assert overdue[0].title == "Overdue"

    def test_summary(self):
        board = Board()
        board.add(Card(title="T1"), "todo")
        board.add(Card(title="T2"), "doing")
        s = board.summary()
        assert s["total_cards"] == 2
        assert s["columns"]["todo"]["count"] == 1
        assert s["columns"]["doing"]["count"] == 1

    def test_add_column(self):
        board = Board()
        board.add_column("review", wip_limit=3)
        assert board.get_column("review") is not None
        assert board.get_column("review").wip_limit == 3

    def test_add_duplicate_column(self):
        board = Board()
        with pytest.raises(ValueError):
            board.add_column("todo")

    def test_remove_column(self):
        board = Board()
        assert board.remove_column("todo") is True
        assert board.get_column("todo") is None
        assert board.remove_column("nonexistent") is False


class TestSerialization:
    def test_save_and_load(self, tmp_path):
        board = Board(name="Test Pano")
        board.add(Card(title="Task 1", priority=Priority.HIGH), "todo")
        board.add(Card(title="Task 2"), "doing")

        path = tmp_path / "board.json"
        board.save(path)

        loaded = Board.load(path)
        assert loaded.name == "Test Pano"
        assert len(loaded.all_cards()) == 2
        assert loaded.get_column("todo").cards[0].title == "Task 1"
        assert loaded.get_column("todo").cards[0].priority == Priority.HIGH

    def test_to_json(self):
        board = Board()
        board.add(Card(title="T"), "todo")
        data = json.loads(board.to_json())
        assert data["columns"][0]["name"] == "todo"
        assert len(data["columns"][0]["cards"]) == 1

    def test_from_dict(self):
        data = {
            "name": "Test",
            "columns": [
                {"name": "todo", "wip_limit": None, "cards": []},
                {"name": "done", "wip_limit": None, "cards": []},
            ],
        }
        board = Board.from_dict(data)
        assert board.name == "Test"
        assert len(board.columns) == 2