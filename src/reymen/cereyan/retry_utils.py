# -*- coding: utf-8 -*-
"""Retry utilities — jittered backoff for decorrelated retries.

Replaces fixed exponential backoff with jittered delays to prevent
thundering-herd retry spikes when multiple sessions hit the same
rate-limited provider concurrently.

Adapted from Hermes Agent (agent/retry_utils.py).
Sifir Hermes bagimliligi — ReYMeN'e ozgu.
"""
from __future__ import annotations

import random
import threading
import time

# Monotonic counter for jitter seed uniqueness within the same process.
_jitter_counter = 0
_jitter_lock = threading.Lock()


def jittered_backoff(
    attempt: int,
    *,
    base_delay: float = 5.0,
    max_delay: float = 120.0,
    jitter_ratio: float = 0.5,
) -> float:
    """Jitter'li exponential backoff suresi hesapla.

    Args:
        attempt: 1-based retry deneme numarasi.
        base_delay: Temel bekleme (saniye).
        max_delay: Maksimum bekleme capasi.
        jitter_ratio: Jitter orani (0.5 = [0, delay*0.5] arasi).

    Returns:
        Bekleme suresi: min(base * 2^(attempt-1), max_delay) + jitter.
    """
    global _jitter_counter
    with _jitter_lock:
        _jitter_counter += 1
        tick = _jitter_counter

    exponent = max(0, attempt - 1)
    if exponent >= 63 or base_delay <= 0:
        delay = max_delay
    else:
        delay = min(base_delay * (2 ** exponent), max_delay)

    seed = (time.time_ns() ^ (tick * 0x9E3779B9)) & 0xFFFFFFFF
    rng = random.Random(seed)
    jitter = rng.uniform(0, jitter_ratio * delay)

    return delay + jitter
