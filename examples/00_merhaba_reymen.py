#!/usr/bin/env python3
"""Ornek 0: ReYMeN'e merhaba de — tek soru, tek cevap."""

from src.reymen.cereyan.beyin import Beyin

beyin = Beyin({"model": {"provider": "deepseek", "model": "deepseek-v4-flash"}})
cevap = beyin.dusun("Merhaba! Kimsin sen?")
print(f"ReYMeN: {cevap}")
