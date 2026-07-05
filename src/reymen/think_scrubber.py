# -*- coding: utf-8 -*-
"""Dusunce bloklarini temizleme.

Hermes agent/think_scrubber.py'den adapte edilmistir.
"""
from __future__ import annotations
import re

def dusunce_temizle(metin: str) -> str:
    """  ve  bloklarini temizle."""
    metin = re.sub(r'<thinking>.*?</thinking>', '', metin, flags=re.DOTALL)
    metin = re.sub(r'<thought>.*?</thought>', '', metin, flags=re.DOTALL)
    metin = re.sub(r'思考.*?思考', '', metin, flags=re.DOTALL)
    return metin.strip()

def dusunce_var_mi(metin: str) -> bool:
    return bool(re.search(r'<(thinking|thought)>', metin, re.IGNORECASE))
