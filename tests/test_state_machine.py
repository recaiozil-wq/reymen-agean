"""Test: reymen/sistem/state_machine.py"""

from __future__ import annotations
import os, sys
from pathlib import Path
import pytest

PROJE_KOK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJE_KOK))


class TestStateMachine:
    def test_import(self):
        from reymen.sistem.state_machine import StateMachine, State

        assert StateMachine is not None

    def test_create(self):
        from reymen.sistem.state_machine import StateMachine

        sm = StateMachine()
        assert sm is not None

    def test_set_state(self):
        from reymen.sistem.state_machine import StateMachine, State

        sm = StateMachine()
        assert sm.set_state(State.THINKING, "test") is True
        assert sm.current == State.THINKING

    def test_status_report(self):
        from reymen.sistem.state_machine import StateMachine

        sm = StateMachine()
        assert isinstance(sm.status_report(), dict)

    def test_heartbeat(self):
        from reymen.sistem.state_machine import StateMachine

        sm = StateMachine()
        sm.heartbeat()
        assert sm.current is not None

    def test_convenience_methods(self):
        from reymen.sistem.state_machine import StateMachine, State

        sm = StateMachine()
        sm.thinking("test")
        assert sm.current == State.THINKING
        sm.idle("done")
        assert sm.current == State.IDLE
        sm.error("fail")
        assert sm.current == State.ERROR
        sm.recover("fixed")
        assert sm.current == State.IDLE or sm.current == State.RECOVERING

    def test_get_history(self):
        from reymen.sistem.state_machine import StateMachine

        sm = StateMachine()
        sm.thinking("test")
        sm.idle("done")
        assert len(sm.get_history(limit=5)) >= 2
