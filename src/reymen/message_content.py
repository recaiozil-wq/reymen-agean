# -*- coding: utf-8 -*-
"""Mesaj icerik isleme.

Hermes agent/message_content.py'den adapte edilmistir.
"""
from __future__ import annotations
from typing import Any, Dict, List

def mesaj_icerigi_al(msg: Dict) -> str:
    icerik = msg.get("content", "")
    if isinstance(icerik, list):
        return " ".join(str(p.get("text","")) for p in icerik if isinstance(p, dict))
    return str(icerik)

def mesajlari_metne_cevir(mesajlar: List[Dict]) -> str:
    return "\n".join(f"{m.get('role','?')}: {mesaj_icerigi_al(m)[:200]}" for m in mesajlar)
