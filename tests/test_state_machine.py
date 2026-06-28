# -*- coding: utf-8 -*-
"""
test_state_machine.py — state_machine.py modülü için pytest testleri.
"""

import sys
import os
import time

# Proje kök dizinini ekle
_proje_kok = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
if _proje_kok not in sys.path:
    sys.path.insert(0, _proje_kok)

import pytest
from state_machine import (
    State,
    StateMachine,
    StateTransitionError,
    _TRANSITIONS,
    _ERROR_STATES,
    _ACTIVE_STATES,
    _STUCK_STATES,
)


# ── State enum testleri ──────────────────────────────────────────────────

class TestStateEnum:
    def test_tum_durumlar_tanimli(self):
        """Tüm State enum değerleri tanımlı."""
        assert State.UNINITIALIZED.value == "uninitialized"
        assert State.INITIALIZING.value == "initializing"
        assert State.IDLE.value == "idle"
        assert State.THINKING.value == "thinking"
        assert State.TOOL_CALL.value == "tool_call"
        assert State.WAITING.value == "waiting"
        assert State.ERROR.value == "error"
        assert State.RECOVERING.value == "recovering"
        assert State.DEGRADED.value == "degraded"
        assert State.SHUTDOWN.value == "shutdown"
        assert State.CRASHED.value == "crashed"

    def test_state_esitlik(self):
        """Aynı State değerleri eşittir."""
        assert State.IDLE == State.IDLE
        assert State.ERROR != State.IDLE


# ── StateMachine başlatma testleri ───────────────────────────────────────

class TestStateMachineInit:
    def test_varsayilan_durum(self):
        """StateMachine varsayılan olarak UNINITIALIZED durumunda başlar."""
        sm = StateMachine()
        assert sm.current == State.UNINITIALIZED

    def test_varsayilan_heartbeat_interval(self):
        """Varsayılan heartbeat interval 30 saniyedir."""
        sm = StateMachine()
        assert sm._heartbeat_interval == 30

    def test_varsayilan_stale_timeout(self):
        """Varsayılan stale timeout 120 saniyedir."""
        sm = StateMachine()
        assert sm._stale_timeout == 120

    def test_ozel_heartbeat_interval(self):
        """Özel heartbeat interval atanabilir."""
        sm = StateMachine(heartbeat_interval_sec=10)
        assert sm._heartbeat_interval == 10

    def test_ozel_stale_timeout(self):
        """Özel stale timeout atanabilir."""
        sm = StateMachine(stale_timeout_sec=60)
        assert sm._stale_timeout == 60

    def test_baslangic_transition_count(self):
        """Başlangıç transition_count 0'dır."""
        sm = StateMachine()
        assert sm.transition_count == 0

    def test_baslangic_state_since(self):
        """state_since başlangıçta bir timestamp'tir."""
        sm = StateMachine()
        assert isinstance(sm.state_since, float)
        assert sm.state_since > 0

    def test_baslangic_bos_gecmis(self):
        """Başlangıçta geçmiş boştur."""
        sm = StateMachine()
        assert sm.get_history() == []


# ── State sorgulama testleri ─────────────────────────────────────────────

class TestStateSorgulama:
    def test_is_idle_true(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        assert sm.is_idle()

    def test_is_idle_false(self):
        sm = StateMachine()
        assert not sm.is_idle()

    def test_is_busy_thinking(self):
        sm = StateMachine()
        sm.set_state(State.THINKING)
        assert sm.is_busy()

    def test_is_busy_tool_call(self):
        sm = StateMachine()
        sm.set_state(State.TOOL_CALL)
        assert sm.is_busy()

    def test_is_busy_false_idle(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        assert not sm.is_busy()

    def test_is_error_true(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert sm.is_error()

    def test_is_error_false(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        assert not sm.is_error()

    def test_is_active_idle(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        assert sm.is_active()

    def test_is_active_error(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert not sm.is_active()

    def test_is_recoverable_error(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert sm.is_recoverable()

    def test_is_recoverable_degraded(self):
        sm = StateMachine()
        sm.set_state(State.DEGRADED)
        assert sm.is_recoverable()

    def test_is_recoverable_idle(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        assert not sm.is_recoverable()

    def test_current_state_duration(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        time.sleep(0.01)
        dur = sm.current_state_duration()
        assert dur > 0.005

    def test_state_since_property(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        assert isinstance(sm.state_since, float)
        assert sm.state_since > 0


# ── State geçiş testleri ─────────────────────────────────────────────────

class TestStateGecisleri:
    def test_uninitialized_to_initializing(self):
        sm = StateMachine()
        assert sm.set_state(State.INITIALIZING)
        assert sm.current == State.INITIALIZING

    def test_initializing_to_idle(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        assert sm.set_state(State.IDLE)

    def test_initializing_to_error(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        assert sm.set_state(State.ERROR)

    def test_initializing_to_shutdown(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        assert sm.set_state(State.SHUTDOWN)

    def test_idle_to_thinking(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.set_state(State.THINKING)

    def test_thinking_to_tool_call(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.THINKING)
        assert sm.set_state(State.TOOL_CALL)

    def test_thinking_to_idle(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.THINKING)
        assert sm.set_state(State.IDLE)

    def test_tool_call_to_thinking(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.THINKING)
        sm.set_state(State.TOOL_CALL)
        assert sm.set_state(State.THINKING)

    def test_tool_call_to_waiting(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.THINKING)
        sm.set_state(State.TOOL_CALL)
        assert sm.set_state(State.WAITING)

    def test_error_to_recovering(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert sm.set_state(State.RECOVERING)

    def test_recovering_to_idle(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        sm.set_state(State.RECOVERING)
        assert sm.set_state(State.IDLE)

    def test_recovering_to_degraded(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        sm.set_state(State.RECOVERING)
        assert sm.set_state(State.DEGRADED)

    def test_crashed_to_initializing(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        sm.set_state(State.CRASHED)
        assert sm.set_state(State.INITIALIZING)

    def test_shutdown_hicbir_yere_gidemez(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.SHUTDOWN)
        assert not sm.set_state(State.IDLE)
        assert not sm.set_state(State.ERROR)
        assert not sm.set_state(State.THINKING)

    def test_gecersiz_gecis_reddedilir(self):
        """IDLE -> CRASHED geçersizdir ve reddedilir."""
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert not sm.set_state(State.CRASHED)
        assert sm.current == State.IDLE

    def test_gecersiz_geciste_durum_degismez(self):
        """Geçersiz geçişte mevcut durum korunur."""
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.SHUTDOWN)
        assert sm.current == State.SHUTDOWN

    def test_ayni_state_gecisi_heartbeat_sayar(self):
        """Aynı state'e geçiş heartbeat olarak sayılır."""
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        onceki = sm._last_heartbeat
        time.sleep(0.01)
        assert sm.set_state(State.IDLE)
        assert sm._last_heartbeat > onceki

    def test_set_state_neden_parametresi_kaydedilir(self):
        """set_state'e verilen neden geçmişe kaydedilir."""
        sm = StateMachine()
        sm.set_state(State.INITIALIZING, "sistem basliyor")
        sm.set_state(State.IDLE, "hazir")
        son = sm.get_history(limit=1)[0]
        assert son["reason"] == "hazir"

    def test_transition_count_artar(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        assert sm.transition_count == 1
        sm.set_state(State.IDLE)
        assert sm.transition_count == 2

    def test_gecersiz_geciste_transition_count_artmaz(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.transition_count == 2
        sm.set_state(State.CRASHED)  # geçersiz
        assert sm.transition_count == 2  # artmamalı

    def test_idle_to_degraded_gecerli(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.set_state(State.DEGRADED)


# ── Heartbeat / Stuck testleri ───────────────────────────────────────────

class TestHeartbeatStuck:
    def test_heartbeat_gunceller(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        onceki = sm._last_heartbeat
        time.sleep(0.01)
        sm.heartbeat()
        assert sm._last_heartbeat > onceki

    def test_aktif_state_stuck_olmaz_henuz(self):
        sm = StateMachine(stale_timeout_sec=120)
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert not sm.is_stuck()

    def test_error_state_stuck(self):
        """ERROR durumu _STUCK_STATES'tedir."""
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert sm.is_stuck()

    def test_shutdown_state_stuck(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.SHUTDOWN)
        assert sm.is_stuck()

    def test_uninitialized_state_stuck(self):
        sm = StateMachine()
        assert sm.is_stuck()

    def test_tick_stuck_return_state(self):
        sm = StateMachine()
        assert sm.tick() == State.UNINITIALIZED

    def test_tick_not_stuck_return_none(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.tick() is None


# ── Callback testleri ────────────────────────────────────────────────────

class TestCallbacks:
    def test_on_transition_cagrilir(self):
        """State değişikliğinde callback tetiklenir."""
        sm = StateMachine()
        cagrildi = []
        def cb(eski, yeni, neden):
            cagrildi.append((eski, yeni, neden))
        sm.on_transition(cb)
        sm.set_state(State.INITIALIZING, "test")
        assert len(cagrildi) == 1
        assert cagrildi[0][0] == State.UNINITIALIZED
        assert cagrildi[0][1] == State.INITIALIZING
        assert cagrildi[0][2] == "test"

    def test_callback_gecersiz_geciste_cagrilmaz(self):
        """Geçersiz geçişte callback çağrılmaz."""
        sm = StateMachine()
        cagrildi = []
        def cb(eski, yeni, neden):
            cagrildi.append((eski, yeni, neden))
        sm.on_transition(cb)
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.CRASHED)  # geçersiz
        assert len(cagrildi) == 2  # sadece INITIALIZING ve IDLE

    def test_birden_cok_callback(self):
        """Birden fazla callback eklenebilir ve tetiklenir."""
        sm = StateMachine()
        sayac = [0, 0]
        def cb1(*_):
            sayac[0] += 1
        def cb2(*_):
            sayac[1] += 1
        sm.on_transition(cb1)
        sm.on_transition(cb2)
        sm.set_state(State.INITIALIZING)
        assert sayac[0] == 1
        assert sayac[1] == 1

    def test_remove_callback(self):
        """Callback kaldırılabilir."""
        sm = StateMachine()
        sayac = [0]
        def cb(*_):
            sayac[0] += 1
        sm.on_transition(cb)
        sm.set_state(State.INITIALIZING)
        assert sayac[0] == 1
        sm.remove_callback(cb)
        sm.set_state(State.IDLE)
        assert sayac[0] == 1  # artmamalı

    def test_callback_hatasi_kirilma_yapmaz(self):
        """Callback hata fırlatırsa state geçişi yine de tamamlanır."""
        sm = StateMachine()
        def hatali_cb(*_):
            raise ValueError("hata")
        sm.on_transition(hatali_cb)
        assert sm.set_state(State.INITIALIZING)
        assert sm.current == State.INITIALIZING


# ── Yardımcı metot testleri ──────────────────────────────────────────────

class TestYardimcilar:
    def test_idle_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        assert sm.idle("hazir")
        assert sm.current == State.IDLE

    def test_error_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.error("hata")
        assert sm.current == State.ERROR

    def test_recover_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert sm.recover("yeniden")
        assert sm.current == State.RECOVERING

    def test_shutdown_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.shutdown("kapanis")
        assert sm.current == State.SHUTDOWN

    def test_crashed_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.ERROR)
        assert sm.crashed("coktu")
        assert sm.current == State.CRASHED

    def test_thinking_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.thinking("dusunuyor")
        assert sm.current == State.THINKING

    def test_tool_call_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.THINKING)
        assert sm.tool_call("arac")
        assert sm.current == State.TOOL_CALL

    def test_waiting_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        sm.set_state(State.THINKING)
        sm.set_state(State.TOOL_CALL)
        assert sm.waiting("bekliyor")
        assert sm.current == State.WAITING

    def test_degraded_yardimcisi(self):
        sm = StateMachine()
        sm.set_state(State.INITIALIZING)
        sm.set_state(State.IDLE)
        assert sm.degraded("kisitli")
        assert sm.current == State.DEGRADED


# ── Status report testleri ───────────────────────────────────────────────

class TestStatusReport:
    def test_status_report_anahtarlar(self):
        """status_report tüm gerekli anahtarları içerir."""
        sm = StateMachine()
        rapor = sm.status_report()
        assert "state" in rapor
        assert "state_since" in rapor
        assert "duration_sec" in rapor
        assert "last_heartbeat_ago" in rapor
        assert "transition_count" in rapor
        assert "is_stuck" in rapor
        assert "is_recoverable" in rapor
        assert "heartbeat_interval" in rapor
        assert "stale_timeout" in rapor

    def test_status_report_dogru_durum(self):
        sm = StateMachine()
        sm.set_state(State.IDLE)
        rapor = sm.status_report()
        assert rapor["state"] == "idle"
        assert rapor["is_stuck"] is False
        assert rapor["is_recoverable"] is False


# ── _TRANSITIONS sabiti testleri ─────────────────────────────────────────

class TestTransitionsSabiti:
    def test_tum_durumlar_anahtar_olarak_var(self):
        """_TRANSITIONS tüm State değerlerini anahtar olarak içerir."""
        for state in State:
            assert state in _TRANSITIONS

    def test_transitions_hepsi_set(self):
        """_TRANSITIONS değerlerinin hepsi set'tir."""
        for k, v in _TRANSITIONS.items():
            assert isinstance(v, set)

    def test_error_states_dogru(self):
        assert State.ERROR in _ERROR_STATES
        assert State.RECOVERING in _ERROR_STATES
        assert State.DEGRADED in _ERROR_STATES
        assert State.CRASHED in _ERROR_STATES
        assert State.IDLE not in _ERROR_STATES

    def test_active_states_dogru(self):
        assert State.IDLE in _ACTIVE_STATES
        assert State.THINKING in _ACTIVE_STATES
        assert State.TOOL_CALL in _ACTIVE_STATES
        assert State.WAITING in _ACTIVE_STATES
        assert State.DEGRADED in _ACTIVE_STATES
        assert State.ERROR not in _ACTIVE_STATES

    def test_stuck_states_dogru(self):
        assert State.UNINITIALIZED in _STUCK_STATES
        assert State.ERROR in _STUCK_STATES
        assert State.SHUTDOWN in _STUCK_STATES
        assert State.CRASHED in _STUCK_STATES
        assert State.IDLE not in _STUCK_STATES
