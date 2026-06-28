# -*- coding: utf-8 -*-
"""gateway/platforms/signal_rate_limit.py — Signal Hiz Sinirlama.

Signal mesajlari arasinda minimum bekleme suresi.
"""

import time
import threading


_signal_son_mesaj = 0.0
_signal_kilit = threading.Lock()
_MIN_BEKLEME = 2.0  # saniye


def bekleme_yap():
    """Signal rate limitine uygun bekleme yap."""
    global _signal_son_mesaj
    with _signal_kilit:
        simdi = time.time()
        gecen = simdi - _signal_son_mesaj
        if gecen < _MIN_BEKLEME:
            bekle = _MIN_BEKLEME - gecen
            time.sleep(bekle)
        _signal_son_mesaj = time.time()
