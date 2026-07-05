# -*- coding: utf-8 -*-
"""
delegation_manager.py -- P2 Delegasyon: Subagent, task decomposition, sonuc toplama.

Mevcut delegasyon sistemleri (reymen/ag/delegasyon.py, reymen/ag/delegation.py)
uzerine kurulmustur. LLM ile gorev ayrismasi, subagent yonetimi,
paralel/zincir modlari, sonuc toplama ve birlestirme.

Motor Tools:
    GOREV_BOL(hedef)            -> Karmasik gorevi alt-gorevlere ayir
    SUB_GOREV_CALISTIR(goal)    -> Subagent calistir
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# --- Mevcut Delegasyon Modullerini dene ---
try:
    from reymen.ag.delegasyon import (
        DelegasyonSistemi as _DelegasyonSistemi,
        SubAgent as _DelegasyonSubAgent,
        SubAgentCalistirici as _SubAgentCalistirici,
        GorevAyristirici as _GorevAyristirici,
    )

    _DELEGASYON_MEVCUT = True
except ImportError:
    _DELEGASYON_MEVCUT = False
