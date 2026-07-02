"""Test: reymen/kanban.py — Board, Card, Column, Priority testleri"""
from __future__ import annotations

import sys
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import pytest

# Proje kokunu path'e ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


@pytest.fixture
def board():
    from reymen.kanban import Board, Card
    b = Board(name="Test Pano")
    yield b


# ── Priority ─────────────────────────────────────────────────────────────

class TestPriority:
    def test_from_str_name(self):
        from reymen.kanban import Priority
        assert Priority.from_str("HIGH") == Priority.HIGH
        assert Priority.from_str("low") == Priority.LOW
        assert Priority.from_str("MEDIUM") == Priority.MEDIUM

    def test_from_str_int(self):
        from reymen.kanban import Priority
        assert Priority.from_str(0) == Priority.CRITICAL
        assert Priority.from_str(3) == Priority.LOW

    def test_from_str_priority_object(self):
        from reymen.kanban import Priority
        assert Priority.from_str(Priority.CRITICAL) == Priority.CRITICAL

    def test_from_str_aliases(self):
        from reymen.kanban import Priority
        assert Priority.from_str("URGENT") == Priority.CRITICAL
        assert Priority.from_str("BLOCKER") == Priority.CRITICAL
        assert Priority.from_str("NORMAL") == Priority.MEDIUM
        assert Priority.from_str("TRIVIAL") == Priority.LOW

    def test_from_str_invalid_raises(self):
        from reymen.kanban import Priority
        with pytest.raises(ValueError, match="Geçersiz"):
            Priority.from_str("INVALID")

    def test_str_representation(self):
        from reymen.kanban import Priority
        assert str(Priority.HIGH) == "HIGH"
        assert str(Priority.BACKLOG) == "BACKLOG"

    def test_enum_ordering(self):
        from reymen.kanban import Priority
        assert Priority.CRITICAL < Priority.HIGH < Priority.MEDIUM < Priority.LOW < Priority.BACKLOG


# ── CardStatus ───────────────────────────────────────────────────────────

class TestCardStatus:
    def test_gecerli_mi_valid_transitions(self):
        from reymen.kanban import CardStatus
        assert CardStatus.gecerli_mi("backlog", "todo") is True
        assert CardStatus.gecerli_mi("backlog", "ready") is True
        assert CardStatus.gecerli_mi("todo", "in_progress") is True
        assert CardStatus.gecerli_mi("in_progress", "blocked") is True
        assert CardStatus.gecerli_mi("in_progress", "review") is True
        assert CardStatus.gecerli_mi("review", "done") is True
        assert CardStatus.gecerli_mi("blocked", "in_progress") is True

    def test_gecerli_mi_invalid_transitions(self):
        from reymen.kanban import CardStatus
        assert CardStatus.gecerli_mi("backlog", "in_progress") is False
        assert CardStatus.gecerli_mi("done", "todo") is False
        assert CardStatus.gecerli_mi("todo", "review") is False
        assert CardStatus.gecerli_mi("ready", "backlog") is False

    def test_gecerli_mi_unknown_source(self):
        from reymen.kanban import CardStatus
        assert CardStatus.gecerli_mi("unknown", "todo") is False


# ── Card ─────────────────────────────────────────────────────────────────

class TestCard:
    def test_card_defaults(self):
        from reymen.kanban import Card
        c = Card(title="Test Kart")
        assert c.title == "Test Kart"
        assert c.status == "backlog"
        assert len(c.id) == 12
        assert c.priority.name == "MEDIUM"

    def test_card_touch_updates_timestamp(self):
        from reymen.kanban import Card
        c = Card(title="Dokunma")
        old = c.updated_at
        c.touch()
        assert c.updated_at >= old

    def test_is_overdue_no_deadline(self):
        from reymen.kanban import Card
        c = Card(title="Surek Yok")
        assert c.is_overdue() is False

    def test_is_overdue_past_deadline(self):
        from reymen.kanban import Card
        c = Card(title="Gecikmis", deadline="2020-01-01T00:00:00+00:00")
        assert c.is_overdue() is True

    def test_is_overdue_future_deadline(self):
        from reymen.kanban import Card
        c = Card(title="Gelecek", deadline="2099-12-31T23:59:59+00:00")
        assert c.is_overdue() is False

    def test_add_comment(self):
        from reymen.kanban import Card
        c = Card(title="Yorum")
        entry = c.add_comment("worker1", "deneme yorum")
        assert entry["author"] == "worker1"
        assert entry["body"] == "deneme yorum"
        assert len(c.comment_thread) == 1
        assert "id" in entry
        assert "timestamp" in entry

    def test_add_heartbeat(self):
        from reymen.kanban import Card
        c = Card(title="HB")
        hb = c.add_heartbeat("calisiyor", "test")
        assert hb["status"] == "calisiyor"
        assert hb["message"] == "test"
        assert len(c.heartbeats) == 1

    def test_start_and_end_run(self):
        from reymen.kanban import Card
        c = Card(title="Run")
        run = c.start_run("worker_1")
        assert run.worker == "worker_1"
        assert run.outcome == "running"
        c.end_run("completed", summary="bitti", error="")
        assert c.runs[-1].outcome == "completed"
        assert c.runs[-1].summary == "bitti"
        assert c.summary == "bitti"

    def test_end_run_with_no_runs(self):
        from reymen.kanban import Card
        c = Card(title="Bosan")
        c.end_run("completed")  # should not raise

    def test_as_dict(self):
        from reymen.kanban import Card, Priority
        c = Card(title="Dict", priority=Priority.LOW)
        d = c.as_dict()
        assert d["title"] == "Dict"
        assert d["priority"] == 3
        assert d["priority_name"] == "LOW"
        assert "runs" in d

    def test_from_dict_roundtrip(self):
        from reymen.kanban import Card, Priority
        original = Card(title="Yuvarlak", priority=Priority.HIGH, description="test")
        d = original.as_dict()
        restored = Card.from_dict(d)
        assert restored.title == "Yuvarlak"
        assert restored.priority == Priority.HIGH
        assert restored.description == "test"


# ── Column ───────────────────────────────────────────────────────────────

class TestColumn:
    def test_add_card(self):
        from reymen.kanban import Column, Card
        col = Column(name="todo")
        c = Card(title="Gorev")
        col.add(c)
        assert len(col.cards) == 1
        assert col.cards[0].title == "Gorev"

    def test_wip_limit_exceeded(self):
        from reymen.kanban import Column, Card
        col = Column(name="wip", wip_limit=1)
        col.add(Card(title="Ilk"))
        with pytest.raises(ValueError, match="WIP"):
            col.add(Card(title="Ikinci"))

    def test_remove_card(self):
        from reymen.kanban import Column, Card
        col = Column(name="test")
        c = Card(title="Sil")
        col.add(c)
        removed = col.remove(c.id)
        assert removed is not None
        assert removed.title == "Sil"
        assert len(col.cards) == 0

    def test_remove_nonexistent(self):
        from reymen.kanban import Column
        col = Column(name="test")
        assert col.remove("yok") is None

    def test_get_card(self):
        from reymen.kanban import Column, Card
        col = Column(name="test")
        c = Card(title="Bul")
        col.add(c)
        assert col.get(c.id).title == "Bul"

    def test_get_nonexistent(self):
        from reymen.kanban import Column
        col = Column(name="test")
        assert col.get("yok") is None

    def test_sort_by_priority(self):
        from reymen.kanban import Column, Card, Priority
        col = Column(name="test")
        col.add(Card(title="Dusuk", priority=Priority.LOW))
        col.add(Card(title="Yuksek", priority=Priority.CRITICAL))
        col.add(Card(title="Orta", priority=Priority.MEDIUM))
        col.sort_by_priority()
        assert col.cards[0].title == "Yuksek"
        assert col.cards[1].title == "Orta"
        assert col.cards[2].title == "Dusuk"

    def test_as_dict(self):
        from reymen.kanban import Column, Card
        col = Column(name="test", wip_limit=5)
        col.add(Card(title="K1"))
        d = col.as_dict()
        assert d["name"] == "test"
        assert d["wip_limit"] == 5
        assert len(d["cards"]) == 1


# ── Board ────────────────────────────────────────────────────────────────

class TestBoard:
    def test_init_default_columns(self):
        from reymen.kanban import Board
        b = Board()
        assert len(b.columns) == 7
        assert b.columns[0].name == "backlog"
        assert b.columns[-1].name == "done"

    def test_add_and_remove_column(self, board):
        board.add_column("test_kolon", wip_limit=3)
        assert board.get_column("test_kolon") is not None
        assert board.get_column("test_kolon").wip_limit == 3
        assert board.remove_column("test_kolon") is True
        assert board.get_column("test_kolon") is None

    def test_add_duplicate_column_raises(self, board):
        with pytest.raises(ValueError, match="zaten var"):
            board.add_column("backlog")

    def test_remove_nonexistent_column(self, board):
        assert board.remove_column("yok") is False

    def test_add_card_to_column(self, board):
        from reymen.kanban import Card
        c = Card(title="Yeni")
        board.add(c, "backlog")
        assert board.find(c.id) is not None
        assert c.status == "backlog"

    def test_add_card_to_invalid_column(self, board):
        from reymen.kanban import Card
        with pytest.raises(ValueError, match="bulunamad"):
            board.add(Card(title="Hata"), "yok_kolon")

    def test_move_card(self, board):
        from reymen.kanban import Card
        c = Card(title="Tasima")
        board.add(c, "backlog")
        board.move(c.id, "todo")
        assert board.find(c.id).status == "todo"

    def test_move_same_column_idempotent(self, board):
        from reymen.kanban import Card
        c = Card(title="Ayni")
        board.add(c, "backlog")
        board.move(c.id, "backlog")
        assert board.find(c.id).status == "backlog"

    def test_move_invalid_transition_raises(self, board):
        from reymen.kanban import Card
        c = Card(title="Gecersiz")
        board.add(c, "backlog")
        with pytest.raises(ValueError, match="Geçersiz durum"):
            board.move(c.id, "in_progress")

    def test_move_nonexistent_card_raises(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.move("yok_id", "todo")

    def test_move_to_nonexistent_column_raises(self, board):
        from reymen.kanban import Card
        c = Card(title="Hedefsiz")
        board.add(c, "backlog")
        # Status gecisi gecersiz oldugu icin "Geçersiz durum" hatasi alinir
        with pytest.raises(ValueError, match="Geçersiz durum"):
            board.move(c.id, "yok_kolon")

    def test_set_status(self, board):
        from reymen.kanban import Card
        c = Card(title="Durum")
        board.add(c, "backlog")
        board.set_status(c.id, "ready")
        assert board.find(c.id).status == "ready"

    def test_prioritize_card(self, board):
        from reymen.kanban import Card, Priority
        c = Card(title="Oncelik", priority=Priority.LOW)
        board.add(c, "backlog")
        board.prioritize(c.id, Priority.CRITICAL)
        assert board.find(c.id).priority == Priority.CRITICAL

    def test_prioritize_nonexistent_raises(self, board):
        from reymen.kanban import Priority
        with pytest.raises(ValueError):
            board.prioritize("yok", Priority.HIGH)

    def test_set_deadline(self, board):
        from reymen.kanban import Card
        c = Card(title="Deadline")
        board.add(c, "backlog")
        board.set_deadline(c.id, "2099-12-31")
        assert board.find(c.id).deadline == "2099-12-31"

    def test_find_nonexistent(self, board):
        assert board.find("yok_id") is None

    def test_all_cards(self, board):
        from reymen.kanban import Card
        board.add(Card(title="K1"), "backlog")
        board.add(Card(title="K2"), "todo")
        board.add(Card(title="K3"), "done")
        assert len(board.all_cards()) == 3

    def test_overdue_cards(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Gec", deadline="2020-01-01T00:00:00+00:00"), "backlog")
        board.add(Card(title="Guncel", deadline="2099-12-31T00:00:00+00:00"), "todo")
        overdue = board.overdue_cards()
        assert len(overdue) == 1
        assert overdue[0].title == "Gec"

    def test_cards_by_assignee(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Ali'nin", assignee="ali"), "in_progress")
        board.add(Card(title="Veli'nin", assignee="veli"), "todo")
        board.add(Card(title="Ali bitti", assignee="ali", status="done"), "done")
        ali_cards = board.cards_by_assignee("ali")
        assert len(ali_cards) == 1
        assert ali_cards[0].title == "Ali'nin"

    def test_claim_card(self, board):
        from reymen.kanban import Card
        c = Card(title="Ustlen")
        board.add(c, "ready")
        board.claim(c.id, "worker_1")
        card = board.find(c.id)
        assert card.assignee == "worker_1"
        assert card.status == "in_progress"
        assert len(card.runs) == 1

    def test_claim_already_assigned_raises(self, board):
        from reymen.kanban import Card
        c = Card(title="Atanmis", assignee="ali")
        board.add(c, "ready")
        with pytest.raises(ValueError, match="zaten"):
            board.claim(c.id, "veli")

    def test_complete_card(self, board):
        from reymen.kanban import Card
        c = Card(title="Bitis")
        board.add(c, "ready")
        board.claim(c.id, "worker_1")  # start_run + in_progress
        board.complete(c.id, summary="tamam", metadata={"files": ["x.py"]})
        card = board.find(c.id)
        assert card.status == "done"
        assert card.metadata.get("files") == ["x.py"]
        assert card.summary == "tamam"

    def test_block_and_unblock(self, board):
        from reymen.kanban import Card
        c = Card(title="Blok")
        board.add(c, "in_progress")
        board.block(c.id, "dis bagimli")
        assert board.find(c.id).status == "blocked"
        assert board.find(c.id).metadata.get("block_reason") == "dis bagimli"
        board.unblock(c.id)
        assert board.find(c.id).status == "in_progress"

    def test_unblock_not_blocked_raises(self, board):
        from reymen.kanban import Card
        c = Card(title="Bloke Degil")
        board.add(c, "backlog")
        with pytest.raises(ValueError, match="bloke durumunda"):
            board.unblock(c.id)

    def test_comment_on_card(self, board):
        from reymen.kanban import Card
        c = Card(title="Yorumlu")
        board.add(c, "backlog")
        entry = board.comment(c.id, "user", "test")
        assert entry["author"] == "user"
        assert entry["body"] == "test"

    def test_heartbeat(self, board):
        from reymen.kanban import Card
        c = Card(title="HB")
        board.add(c, "in_progress")
        hb = board.heartbeat(c.id, "worker", "calisiyor")
        assert hb["status"] == "worker"

    def test_save_and_load_json(self, board, tmp_path):
        from reymen.kanban import Card, Board
        board.add(Card(title="Kayit"), "backlog")
        p = tmp_path / "board.json"
        board.save(p)
        assert p.exists()
        loaded = Board.load(p)
        assert loaded.name == "Test Pano"
        assert len(loaded.all_cards()) == 1

    def test_to_json(self, board):
        from reymen.kanban import Card
        board.add(Card(title="JSON"), "backlog")
        js = board.to_json()
        data = json.loads(js)
        assert data["name"] == "Test Pano"
        assert len(data["columns"]) == 7

    def test_board_from_dict(self):
        from reymen.kanban import Board
        data = {
            "name": "Yuklenen",
            "columns": [
                {"name": "backlog", "wip_limit": None, "cards": []},
                {"name": "done", "wip_limit": None, "cards": []},
            ],
        }
        b = Board.from_dict(data)
        assert b.name == "Yuklenen"
        assert len(b.columns) == 2

    def test_board_as_dict(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Test"), "backlog")
        d = board.as_dict()
        assert d["name"] == "Test Pano"
        assert len(d["columns"]) == 7

    def test_summary(self, board):
        from reymen.kanban import Card
        board.add(Card(title="T1"), "backlog")
        board.add(Card(title="T2"), "done")
        s = board.summary()
        assert s["name"] == "Test Pano"
        assert s["total_cards"] == 2
        assert s["columns"]["backlog"]["count"] == 1
        assert s["columns"]["done"]["count"] == 1


# ── RunRecord ────────────────────────────────────────────────────────────

class TestRunRecord:
    """RunRecord serilestirme ve deserilestirme."""

    def test_as_dict(self):
        from reymen.kanban import RunRecord
        run = RunRecord(worker="w1", started_at="2024-01-01T00:00:00",
                        ended_at="2024-01-01T01:00:00", outcome="completed",
                        summary="bitti", error="")
        d = run.as_dict()
        assert d["worker"] == "w1"
        assert d["outcome"] == "completed"
        assert d["summary"] == "bitti"
        assert d["heartbeats"] == []

    def test_from_dict(self):
        from reymen.kanban import RunRecord
        data = {
            "worker": "w2",
            "started_at": "2024-01-01T00:00:00",
            "ended_at": "2024-01-01T01:00:00",
            "outcome": "completed",
            "summary": "tamam",
            "error": "",
            "heartbeats": [],
            "extra_field": "should_be_ignored",
        }
        run = RunRecord.from_dict(data)
        assert run.worker == "w2"
        assert run.outcome == "completed"
        assert run.summary == "tamam"
        assert not hasattr(run, "extra_field")

    def test_card_start_end_run_record(self):
        """Kart uzerinden RunRecord olusturma ve serilestirme."""
        from reymen.kanban import Card
        c = Card(title="RR Test")
        run = c.start_run("worker_x")
        assert run.outcome == "running"
        c.end_run("completed", summary="bitti", error="bos")
        assert c.runs[-1].outcome == "completed"

        # as_dict uzerinden dogrulama
        d = c.as_dict()
        assert len(d["runs"]) == 1
        assert d["runs"][0]["outcome"] == "completed"
        assert d["runs"][0]["worker"] == "worker_x"


# ── Card.from_dict ek testler ───────────────────────────────────────────

class TestCardFromDict:
    """Card.from_dict cesitli senaryolar."""

    def test_from_dict_with_runs(self):
        from reymen.kanban import Card, Priority, RunRecord
        data = {
            "title": "Kart",
            "priority": 0,
            "runs": [
                {"worker": "w1", "started_at": "2024-01-01T00:00:00",
                 "ended_at": None, "outcome": "running", "summary": "",
                 "error": "", "heartbeats": []},
            ],
        }
        c = Card.from_dict(data)
        assert c.title == "Kart"
        assert c.priority == Priority.CRITICAL
        assert len(c.runs) == 1
        assert c.runs[0].worker == "w1"

    def test_from_dict_priority_str(self):
        from reymen.kanban import Card, Priority
        data = {"title": "PrioStr", "priority": "HIGH"}
        c = Card.from_dict(data)
        assert c.priority == Priority.HIGH


# ── Board.link ───────────────────────────────────────────────────────────

class TestBoardLink:
    """Board.link metodu testleri."""

    def test_link_parent_child(self, board):
        from reymen.kanban import Card
        parent = Card(title="Parent")
        child = Card(title="Child")
        board.add(parent, "backlog")
        board.add(child, "todo")
        board.link(parent.id, child.id)
        assert child.id in parent.children
        assert parent.id in child.parents

    def test_link_nonexistent_parent(self, board):
        from reymen.kanban import Card
        child = Card(title="Child")
        board.add(child, "todo")
        with pytest.raises(ValueError, match="bulunamad"):
            board.link("yok_id", child.id)

    def test_link_nonexistent_child(self, board):
        from reymen.kanban import Card
        parent = Card(title="Parent")
        board.add(parent, "backlog")
        with pytest.raises(ValueError, match="bulunamad"):
            board.link(parent.id, "yok_id")

    def test_link_idempotent(self, board):
        """Aynı bağ iki kez eklenirse sorun olmaz."""
        from reymen.kanban import Card
        p = Card(title="P")
        c = Card(title="C")
        board.add(p, "backlog")
        board.add(c, "todo")
        board.link(p.id, c.id)
        board.link(p.id, c.id)  # ikinci kez
        assert c.id in p.children
        assert len(p.children) == 1
        assert len(c.parents) == 1


# ── Board.query ──────────────────────────────────────────────────────────

class TestBoardQuery:
    """Board.query metodu testleri."""

    def test_query_no_filters(self, board):
        from reymen.kanban import Card
        board.add(Card(title="K1"), "backlog")
        board.add(Card(title="K2"), "done")
        results = board.query()
        assert len(results) == 2

    def test_query_by_status(self, board):
        from reymen.kanban import Card
        board.add(Card(title="B1"), "backlog")
        board.add(Card(title="B2"), "todo")
        board.add(Card(title="B3"), "todo")
        r = board.query(status="todo")
        assert len(r) == 2
        assert all(c.status == "todo" for c in r)

    def test_query_by_assignee(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Ali1", assignee="ali"), "backlog")
        board.add(Card(title="Ali2", assignee="ali"), "todo")
        board.add(Card(title="Veli1", assignee="veli"), "backlog")
        r = board.query(assignee="ali")
        assert len(r) == 2

    def test_query_by_tag(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Bug", tags=["bug", "frontend"]), "backlog")
        board.add(Card(title="Feature", tags=["feature"]), "backlog")
        r = board.query(tag="bug")
        assert len(r) == 1
        assert r[0].title == "Bug"

    def test_query_overdue(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Gec", deadline="2020-01-01T00:00:00+00:00"), "backlog")
        board.add(Card(title="Guncel", deadline="2099-12-31T00:00:00+00:00"), "todo")
        r = board.query(overdue=True)
        assert len(r) == 1
        assert r[0].title == "Gec"

    def test_query_limit(self, board):
        from reymen.kanban import Card
        for i in range(10):
            board.add(Card(title=f"K{i}"), "backlog")
        r = board.query(limit=3)
        assert len(r) == 3

    def test_query_sort_by_priority(self, board):
        from reymen.kanban import Card, Priority
        c1 = Card(title="Low", priority=Priority.LOW)
        c2 = Card(title="High", priority=Priority.HIGH)
        board.add(c1, "backlog")
        board.add(c2, "backlog")
        r = board.query()
        assert r[0].title == "High"
        assert r[1].title == "Low"


# ── _auto_promote_children ─────────────────────────────────────────────

class TestAutoPromote:
    """_auto_promote_children tam dal coverage."""

    def test_auto_promote_done_card_with_children(self, board):
        from reymen.kanban import Card
        parent = Card(title="Parent")
        child = Card(title="Child")
        board.add(parent, "todo")
        board.add(child, "todo")
        board.link(parent.id, child.id)

        # Parent'i done yap
        board.complete(parent.id, summary="bitti")
        assert board.find(parent.id).status == "done"

        # Child ready'e alinmali
        child_card = board.find(child.id)
        assert child_card.status == "ready"

    def test_auto_promote_not_all_parents_done(self, board):
        """Child'in tum parent'lari done degilse ready'e alinmaz."""
        from reymen.kanban import Card
        p1 = Card(title="P1")
        p2 = Card(title="P2")
        child = Card(title="Child")
        board.add(p1, "todo")
        board.add(p2, "todo")
        board.add(child, "todo")
        board.link(p1.id, child.id)
        board.link(p2.id, child.id)

        # Sadece bir parent'i done yap
        board.complete(p1.id, summary="bitti")

        # Child hala todo
        assert board.find(child.id).status == "todo"

    def test_auto_promote_none_done_card(self, board):
        """Done olmayan kart icin _auto_promote_children hicbir sey yapmaz."""
        from reymen.kanban import Card
        c = Card(title="Todo")
        board.add(c, "todo")
        board._auto_promote_children(c.id)  # hata firlatmamali
        assert board.find(c.id).status == "todo"

    def test_auto_promote_nonexistent_card(self, board):
        """Var olmayan kart icin _auto_promote_children hata firlatmaz."""
        board._auto_promote_children("yok_id")  # hata firlatmamali

    def test_auto_promote_child_not_todo(self, board):
        """Child todo degilse ready'e alinmaz."""
        from reymen.kanban import Card
        parent = Card(title="P")
        child = Card(title="C")
        board.add(parent, "backlog")
        board.add(child, "in_progress")
        board.link(parent.id, child.id)
        board.complete(parent.id, summary="bitti")
        assert board.find(child.id).status == "in_progress"


# ── Board move / set_status ek testler ─────────────────────────────────

class TestBoardMoveExtended:
    """Board.move ve set_status icin ek testler."""

    def test_move_to_target_column_not_found(self, board):
        """move()'de hedef kolon bulunamazsa hata."""
        from reymen.kanban import Card
        c = Card(title="Hedefsiz")
        board.add(c, "backlog")
        # Status gecisi gecersiz oldugu icin 'Geçersiz durum' hatasi alinir
        with pytest.raises(ValueError, match="Geçersiz durum"):
            board.move(c.id, "yok_kolon")

    def test_set_deadline_nonexistent(self, board):
        with pytest.raises(ValueError):
            board.set_deadline("yok", "2099-01-01")

    def test_claim_nonexistent(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.claim("yok", "worker")

    def test_complete_nonexistent(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.complete("yok")

    def test_block_nonexistent(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.block("yok", "sebep")

    def test_unblock_nonexistent(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.unblock("yok")

    def test_comment_nonexistent(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.comment("yok", "user", "test")

    def test_heartbeat_nonexistent(self, board):
        with pytest.raises(ValueError, match="bulunamad"):
            board.heartbeat("yok", "worker", "test")


# ── WIP limit ────────────────────────────────────────────────────────────

class TestWIPLimit:
    """Gecersiz WIP limit degerleri ve sinir durumlari."""

    def test_wip_limit_exact(self, board):
        from reymen.kanban import Card, Column
        col = Column(name="wip", wip_limit=2)
        col.add(Card(title="K1"))
        col.add(Card(title="K2"))
        assert len(col.cards) == 2

    def test_wip_limit_zero(self, board):
        from reymen.kanban import Card, Column
        col = Column(name="zero", wip_limit=0)
        with pytest.raises(ValueError, match="WIP"):
            col.add(Card(title="Ilk"))

    def test_column_add_orders(self, board):
        from reymen.kanban import Card, Column
        col = Column(name="sirali")
        c1 = Card(title="Ilk")
        c2 = Card(title="Ikinci")
        col.add(c1)
        col.add(c2)
        assert c1.order == 0
        assert c2.order == 1


# ── Board serialization ─────────────────────────────────────────────────

class TestBoardSerialization:
    """Board serilestirme roundtrip ve hata senaryolari."""

    def test_board_save_load_roundtrip(self, board, tmp_path):
        from reymen.kanban import Card, Board, Priority
        board.add(Card(title="K1", tags=["test"]), "backlog")
        board.add(Card(title="K2", priority=Priority.CRITICAL), "todo")
        p = tmp_path / "roundtrip.json"
        board.save(p)

        loaded = Board.load(p)
        assert loaded.name == "Test Pano"
        assert len(loaded.all_cards()) == 2

    def test_load_json_error(self, tmp_path):
        from reymen.kanban import Board
        p = tmp_path / "bad.json"
        p.write_text("{invalid json}", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            Board.load(p)

    def test_load_file_not_found(self, tmp_path):
        from reymen.kanban import Board
        with pytest.raises(FileNotFoundError):
            Board.load(tmp_path / "nonexistent.json")

    def test_from_dict_with_cards(self):
        from reymen.kanban import Board
        data = {
            "name": "Dolu Pano",
            "columns": [
                {
                    "name": "backlog",
                    "wip_limit": None,
                    "cards": [
                        {"title": "Kart1", "priority": "MEDIUM"},
                        {"title": "Kart2", "priority": "HIGH"},
                    ],
                },
                {"name": "done", "wip_limit": None, "cards": []},
            ],
        }
        b = Board.from_dict(data)
        assert len(b.all_cards()) == 2
        assert b.all_cards()[0].title == "Kart1"


# ── cards_by_assignee ────────────────────────────────────────────────────

class TestCardsByAssignee:
    def test_no_matches(self, board):
        assert board.cards_by_assignee("yok") == []

    def test_done_cards_excluded(self, board):
        from reymen.kanban import Card
        board.add(Card(title="Bitti", assignee="ali", status="done"), "done")
        assert board.cards_by_assignee("ali") == []


# ── Board summary ────────────────────────────────────────────────────────

class TestBoardSummary:
    def test_summary_over_limit(self, board):
        from reymen.kanban import Card
        board.add_column("wip_test", wip_limit=1)
        col = board.get_column("wip_test")
        # WIP limit atlamak icin dogrudan cards listesine ekle
        col.cards.append(Card(title="K1"))
        col.cards.append(Card(title="K2"))
        s = board.summary()
        assert s["columns"]["wip_test"]["over_limit"] is True


# ── Worker API ──────────────────────────────────────────────────────────

class TestWorkerAPI:
    """Worker API fonksiyonlari (kanban_create, kanban_show, vb.)."""

    def test_kanban_create(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create
        import reymen.kanban as kb

        # _VARSAYILAN_PANO_YOLU'nu gecici yola yonlendir
        temp_pano = tmp_path / "test_board.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Test Kart", description="Aciklama",
                                 assignee="worker1", priority="HIGH",
                                 tags=["test"], deadline="2099-12-31")
        assert card_id is not None
        assert len(card_id) == 12
        assert temp_pano.exists()

    def test_kanban_create_with_parents(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board2.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        # Once bir kart olustur
        parent_id = kanban_create("Parent Kart")
        # Child kart olustur
        child_id = kanban_create("Child Kart", parents=[parent_id])
        assert child_id is not None

    def test_kanban_show(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_show
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board3.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Gosterilecek", description="detay")
        result = kanban_show(card_id)
        assert "Gosterilecek" in result
        assert card_id in result

    def test_kanban_show_not_found(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_show
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board4.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_show("yok_kart")
        assert "bulunamad" in result

    def test_kanban_complete(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_complete
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board5.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Tamamlanacak")
        result = kanban_complete(card_id, summary="bitti", metadata='{"files":["x.py"]}')
        assert "tamamland" in result

    def test_kanban_block(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_claim, kanban_block
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board6.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Bloklanacak")
        kanban_claim(card_id, "worker1")  # once claim -> in_progress
        result = kanban_block(card_id, "dis bagimli")
        assert "bloke edildi" in result

    def test_kanban_block_not_found(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_block
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board7.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_block("yok", "sebep")
        assert "bulunamad" in result

    def test_kanban_unblock(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_claim, kanban_block, kanban_unblock
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board8.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Unblock")
        kanban_claim(card_id, "worker1")  # once claim -> in_progress
        kanban_block(card_id, "sebep")
        result = kanban_unblock(card_id)
        assert "blokesi kald" in result

    def test_kanban_unblock_not_found(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_unblock
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board9.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_unblock("yok")
        assert "bulunamad" in result

    def test_kanban_comment(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_comment
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board10.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Yorum")
        result = kanban_comment(card_id, "test yorum")
        assert "Yorum eklendi" in result

    def test_kanban_comment_not_found(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_comment
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board11.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_comment("yok", "test")
        assert "bulunamad" in result

    def test_kanban_heartbeat(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_heartbeat
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board12.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("HB")
        result = kanban_heartbeat(card_id, "worker1", "calisiyor")
        assert "Heartbeat" in result

    def test_kanban_heartbeat_not_found(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_heartbeat
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board13.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_heartbeat("yok", "w", "test")
        assert "bulunamad" in result

    def test_kanban_claim(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_claim
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board14.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Claim", assignee="worker1")
        result = kanban_claim(card_id, "worker1")
        assert "->" in result

    def test_kanban_list(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_list
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board15.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        kanban_create("Liste1")
        kanban_create("Liste2")
        result = kanban_list()
        assert "2 kart" in result

    def test_kanban_list_filtered(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_list
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board16.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        kanban_create("K1")
        # Varsayilan kolon "todo" oldugu icin
        result = kanban_list(status="todo")
        assert "1 kart" in result

    def test_kanban_list_no_results(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_list
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board17.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_list()
        assert "Kart bulunamad" in result

    def test_kanban_summary(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_summary
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board18.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        kanban_create("S1")
        result = kanban_summary()
        assert "Toplam kart" in result
        assert "ReYMeN Kanban" in result

    def test_kanban_delete(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_create, kanban_delete_card
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board19.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Silinecek")
        result = kanban_delete_card(card_id)
        assert "silindi" in result

    def test_kanban_delete_not_found(self, tmp_path, monkeypatch):
        from reymen.kanban import kanban_delete_card
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board20.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        result = kanban_delete_card("yok")
        assert "bulunamad" in result

    def test_kanban_show_with_metadata_comments(self, tmp_path, monkeypatch):
        """kanban_show'un metadata, yorum ve run icerdigi durum."""
        from reymen.kanban import kanban_create, kanban_show, kanban_comment, kanban_claim, kanban_complete
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board21.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        card_id = kanban_create("Detayli", description="zengin")
        kanban_comment(card_id, "kullanici1")
        kanban_claim(card_id, "worker1")
        kanban_complete(card_id, summary="bitti", metadata='{"anahtar": "deger"}')
        result = kanban_show(card_id)
        assert "Detayli" in result
        assert "kullanici1" in result
        assert "bitti" in result
        assert "anahtar" in result

    def test_kanban_show_with_parents_children(self, tmp_path, monkeypatch):
        """kanban_show parent-child bilgilerini gosterir."""
        from reymen.kanban import kanban_create, kanban_show
        import reymen.kanban as kb

        temp_pano = tmp_path / "test_board22.json"
        monkeypatch.setattr(kb, "_VARSAYILAN_PANO_YOLU", temp_pano)

        parent_id = kanban_create("Ebeveyn")
        child_id = kanban_create("Cocuk", parents=[parent_id])
        result = kanban_show(child_id)
        assert "Bağımlı olduğu" in result
        assert "Ebeveyn" in result

        result = kanban_show(parent_id)
        assert "Alt kartlar" in result
        assert "Cocuk" in result


# ── Motor kaydi ─────────────────────────────────────────────────────────

class TestKanbanMotorKaydet:
    """kanban.motor_kaydet fonksiyonu (ikinci versiyon - 6 tool)."""

    def test_motor_kaydet_is_callable(self):
        from reymen.kanban import motor_kaydet
        assert callable(motor_kaydet)


# ── Board save/load extended ────────────────────────────────────────────

class TestBoardSaveLoadExtended:
    """Board.save ve Board.load icin ek testler."""

    def test_board_save_with_empty_board(self, tmp_path):
        from reymen.kanban import Board
        b = Board(name="Bos Pano")
        p = tmp_path / "bos.json"
        b.save(p)
        loaded = Board.load(p)
        assert loaded.name == "Bos Pano"
        assert len(loaded.all_cards()) == 0

    def test_board_save_with_priority_cards(self, tmp_path):
        from reymen.kanban import Board, Card, Priority
        b = Board(name="Oncelik Pano")
        b.add(Card(title="Yuksek", priority=Priority.HIGH), "backlog")
        b.add(Card(title="Dusuk", priority=Priority.LOW), "backlog")
        p = tmp_path / "prio.json"
        b.save(p)
        loaded = Board.load(p)
        cards = loaded.all_cards()
        assert len(cards) == 2


# ── Board with deadline ─────────────────────────────────────────────────

class TestBoardDeadlineExtended:
    def test_set_deadline_finds_card(self, board):
        from reymen.kanban import Card
        c = Card(title="Sureli")
        board.add(c, "backlog")
        board.set_deadline(c.id, "2099-12-31")
        assert board.find(c.id).deadline == "2099-12-31"


# ── Card.is_override_with_custom_now ────────────────────────────────────

class TestCardIsOverdue:
    def test_is_overdue_custom_now(self):
        from reymen.kanban import Card
        # String comparison works for ISO format dates: '2020' < '2099' is True
        c = Card(title="Gecikmis", deadline="2020-01-01T00:00:00+00:00")
        # Deadline 2020, now is 2019 -> not overdue (deadline > now)
        assert c.is_overdue("2019-01-01T00:00:00+00:00") is False
        # Deadline 2020, now is 2099 -> overdue (deadline < now)
        assert c.is_overdue("2099-01-01T00:00:00+00:00") is True
