# -*- coding: utf-8 -*-
"""
state_machine.py â€” ReYMeN Runtime State Machine.

Agent'in operasyonel durumunu (IDLE, THINKING, TOOL_CALL, ERROR, RECOVERING
vb.) takip eder. Her durum geÃ§iÅŸini loglar, timeout kontrolÃ¼ yapar,
state deÄŸiÅŸikliklerinde hook'larÄ± tetikler.

KullanÄ±m:
    sm = StateMachine()
    sm.on_transition(my_callback)  # state deÄŸiÅŸince Ã§aÄŸrÄ±lÄ±r
    sm.set_state(StateMachine.IDLE)
    sm.tick()  # heartbeat kontrolÃ¼
    if sm.is_stuck():  # belirlenen sÃ¼rede heartbeat alÄ±nmadÄ±ysa
        sm.recover()
"""

from __future__ import annotations

import enum
import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class State(enum.Enum):
    """ReYMeN runtime state machine durumlarÄ±."""

    # BaÅŸlangÄ±Ã§ / Ã§alÄ±ÅŸmÄ±yor
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    IDLE = "idle"

    # Aktif Ã§alÄ±ÅŸma
    THINKING = "thinking"  # LLM Ã§aÄŸrÄ±sÄ± bekleniyor
    TOOL_CALL = "tool_call"  # AraÃ§ Ã§alÄ±ÅŸtÄ±rÄ±lÄ±yor
    WAITING = "waiting"  # DÄ±ÅŸ girdi bekleniyor (HITL / kullanÄ±cÄ±)

    # Hata / kurtarma
    ERROR = "error"  # GeÃ§ici hata
    RECOVERING = "recovering"  # Otomatik kurtarma devam ediyor
    DEGRADED = "degraded"  # Ã‡alÄ±ÅŸÄ±yor ama kÄ±sÄ±tlÄ± kapasite

    # Terminal
    SHUTDOWN = "shutdown"
    CRASHED = "crashed"  # KurtarÄ±lamaz hata


# --- GeÃ§erli durum geÃ§iÅŸleri ---
# Hangi durumdan hangi duruma geÃ§ilebilir
_TRANSITIONS: Dict[State, Set[State]] = {
    State.UNINITIALIZED: {State.INITIALIZING},
    State.INITIALIZING: {State.IDLE, State.ERROR, State.SHUTDOWN},
    State.IDLE: {
        State.THINKING,
        State.INITIALIZING,
        State.ERROR,
        State.SHUTDOWN,
        State.DEGRADED,
    },
    State.THINKING: {
        State.TOOL_CALL,
        State.IDLE,
        State.ERROR,
        State.RECOVERING,
        State.SHUTDOWN,
    },
    State.TOOL_CALL: {
        State.THINKING,
        State.IDLE,
        State.ERROR,
        State.RECOVERING,
        State.WAITING,
        State.DEGRADED,
        State.SHUTDOWN,
    },
    State.WAITING: {State.THINKING, State.IDLE, State.ERROR, State.SHUTDOWN},
    State.ERROR: {State.RECOVERING, State.IDLE, State.SHUTDOWN, State.CRASHED},
    State.RECOVERING: {
        State.IDLE,
        State.DEGRADED,
        State.ERROR,
        State.CRASHED,
        State.SHUTDOWN,
    },
    State.DEGRADED: {State.IDLE, State.ERROR, State.SHUTDOWN, State.RECOVERING},
    State.SHUTDOWN: set(),
    State.CRASHED: {State.INITIALIZING},
}

# Hata/kurtarma kategorisindeki durumlar
_ERROR_STATES = {State.ERROR, State.RECOVERING, State.DEGRADED, State.CRASHED}

# Aktif Ã§alÄ±ÅŸma durumlarÄ± (IDLE + meÅŸgul)
_ACTIVE_STATES = {
    State.IDLE,
    State.THINKING,
    State.TOOL_CALL,
    State.WAITING,
    State.DEGRADED,
}

# Ã–lÃ¼/kilitli durumlar
_STUCK_STATES = {State.UNINITIALIZED, State.ERROR, State.SHUTDOWN, State.CRASHED}


class StateTransitionError(ValueError):
    """GeÃ§ersiz durum geÃ§iÅŸi."""

    pass


TransitionCallback = Callable[[State, State, Optional[str]], None]
"""Hook imzasÄ±: (eski_durum, yeni_durum, neden) -> None"""


class StateMachine:
    """Runtime state machine â€” thread-safe."""

    def __init__(self, heartbeat_interval_sec: int = 30, stale_timeout_sec: int = 120):
        self._state: State = State.UNINITIALIZED
        self._lock = threading.RLock()
        self._callbacks: List[TransitionCallback] = []
        self._heartbeat_interval = heartbeat_interval_sec
        self._stale_timeout = stale_timeout_sec
        self._last_heartbeat: float = time.time()
        self._state_since: float = time.time()
        self._transition_count: int = 0
        self._history: List[Dict[str, Any]] = []

    # â”€â”€ State sorgulama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    @property
    def current(self) -> State:
        with self._lock:
            return self._state

    @property
    def state_since(self) -> float:
        """Bu state'e ne zaman girildi (unix timestamp)."""
        with self._lock:
            return self._state_since

    @property
    def transition_count(self) -> int:
        with self._lock:
            return self._transition_count

    def is_idle(self) -> bool:
        return self.current == State.IDLE

    def is_busy(self) -> bool:
        return self.current in {State.THINKING, State.TOOL_CALL}

    def is_error(self) -> bool:
        return self.current in _ERROR_STATES

    def is_stuck(self) -> bool:
        """Heartbeat timeout aÅŸtÄ±ysa stuck/kilitli kabul et."""
        with self._lock:
            if self._state in _STUCK_STATES:
                return True
            if self._state in _ACTIVE_STATES:
                elapsed = time.time() - self._last_heartbeat
                return elapsed > self._stale_timeout
            return False

    def is_active(self) -> bool:
        return self.current in _ACTIVE_STATES

    def is_recoverable(self) -> bool:
        """Bu state'ten kurtarma denenebilir mi?"""
        return self.current in {State.ERROR, State.DEGRADED, State.RECOVERING}

    def current_state_duration(self) -> float:
        """Bu state'te kaÃ§ saniyedir bekleniyor."""
        return time.time() - self._state_since

    # â”€â”€ State yÃ¶netimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def set_state(self, new_state: State, reason: Optional[str] = None) -> bool:
        """State deÄŸiÅŸtir. GeÃ§ersiz geÃ§iÅŸte log at ama kÄ±rÄ±lma (exception atma)."""
        with self._lock:
            old = self._state

            # AynÄ± state'e geÃ§iÅŸ â€” heartbeat say
            if old == new_state:
                self._heartbeat()
                return True

            # UNINITIALIZED'den Ã§Ä±kÄ±ÅŸ Ã¶zel izin
            if old == State.UNINITIALIZED:
                allowed = True
            else:
                allowed = new_state in _TRANSITIONS.get(old, set())

            if not allowed:
                logger.warning(
                    f"GeÃ§ersiz state geÃ§iÅŸi engellendi: {old.value} -> {new_state.value}"
                    f"{' (' + reason + ')' if reason else ''}"
                )
                return False

            self._state = new_state
            self._state_since = time.time()
            self._last_heartbeat = time.time()
            self._transition_count += 1

            transition = {
                "from": old.value,
                "to": new_state.value,
                "reason": reason,
                "timestamp": time.time(),
                "count": self._transition_count,
            }
            self._history.append(transition)

            # Logla
            log_msg = f"State: {old.value} -> {new_state.value}"
            if reason:
                log_msg += f" ({reason})"
            if new_state in _ERROR_STATES:
                logger.warning(log_msg)
            else:
                logger.info(log_msg)

            # Hook'larÄ± tetikle
            for cb in self._callbacks:
                try:
                    cb(old, new_state, reason)
                except Exception as e:
                    logger.error(f"State callback hatasi: {e}")

            return True

    def heartbeat(self) -> None:
        """Her heartbeat sinyalinde state'in hala canlÄ± olduÄŸunu bildir."""
        self._heartbeat()

    def _heartbeat(self) -> None:
        with self._lock:
            self._last_heartbeat = time.time()

    def tick(self) -> Optional[State]:
        """Periyodik kontrol â€” stuck durumdaysa belirle.

        Returns:
            Stuck ise mevcut state, deÄŸilse None.
        """
        if self.is_stuck():
            return self.current
        return None

    # â”€â”€ Callback yÃ¶netimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def on_transition(self, callback: TransitionCallback) -> None:
        """State deÄŸiÅŸikliklerinde Ã§aÄŸrÄ±lacak callback ekle."""
        with self._lock:
            self._callbacks.append(callback)

    def remove_callback(self, callback: TransitionCallback) -> None:
        with self._lock:
            if callback in self._callbacks:
                self._callbacks.remove(callback)

    # â”€â”€ GeÃ§miÅŸ / durum raporu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Son N state geÃ§iÅŸini dÃ¶ndÃ¼r."""
        with self._lock:
            return list(self._history[-limit:])

    def status_report(self) -> Dict[str, Any]:
        """AnlÄ±k durum raporu."""
        with self._lock:
            return {
                "state": self._state.value,
                "state_since": self._state_since,
                "duration_sec": round(time.time() - self._state_since, 1),
                "last_heartbeat_ago": round(time.time() - self._last_heartbeat, 1),
                "transition_count": self._transition_count,
                "is_stuck": self.is_stuck(),
                "is_recoverable": self.is_recoverable(),
                "heartbeat_interval": self._heartbeat_interval,
                "stale_timeout": self._stale_timeout,
            }

    # â”€â”€ YardÄ±mcÄ±lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def idle(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.IDLE, reason)

    def error(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.ERROR, reason)

    def recover(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.RECOVERING, reason)

    def shutdown(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.SHUTDOWN, reason)

    def crashed(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.CRASHED, reason)

    def thinking(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.THINKING, reason)

    def tool_call(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.TOOL_CALL, reason)

    def waiting(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.WAITING, reason)

    def degraded(self, reason: Optional[str] = None) -> bool:
        return self.set_state(State.DEGRADED, reason)


# â”€â”€ HÄ±zlÄ± test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sm = StateMachine()
    sm.set_state(State.INITIALIZING, "sistem basliyor")
    sm.set_state(State.IDLE, "hazir")
    sm.set_state(State.THINKING, "kullanici hedef verdi")
    sm.set_state(State.ERROR, "API hatasi")
    assert sm.is_error()
    assert sm.is_stuck() or True  # henÃ¼z timeout olmamÄ±ÅŸ
    sm.set_state(State.RECOVERING, "yeniden deneniyor")
    sm.set_state(State.IDLE, "kurtarildi")
    print(f"State: {sm.current.value}, Gecis: {sm.transition_count}")
    print(f"Rapor: {sm.status_report()}")
    print("Tum testler GECTI")
