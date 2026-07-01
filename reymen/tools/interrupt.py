"""ReYMeN tools.interrupt stub — her zaman False döner (Hermes bağımsız)."""

import os

_DEBUG_INTERRUPT = bool(os.getenv("HERMES_DEBUG_INTERRUPT"))

_thread_local = None  # type: ignore


def is_interrupted() -> bool:
    """ReYMeN'de interrupt mekanizması yok — her zaman False."""
    return False


def set_interrupt(thread_id: int) -> None:
    pass


def clear_interrupt() -> None:
    pass
