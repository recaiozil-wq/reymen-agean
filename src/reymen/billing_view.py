# -*- coding: utf-8 -*-
"""Fatura goruntuleme.

Hermes agent/billing_view.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

def maliyet_raporu(oturum_sayisi: int = 0, toplam_token: int = 0) -> str:
    return f"Oturum: {oturum_sayisi}, Token: {toplam_token}, Maliyet: ~${toplam_token * 0.000002:.4f}"
