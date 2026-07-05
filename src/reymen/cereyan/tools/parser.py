# -*- coding: utf-8 -*-
"""Tool call ayristirma ve yanit temizleme.

conversation_loop.py'den extract edilmistir.
"""
from __future__ import annotations

import re
import uuid
from typing import List


# Gongoru bitti tetikleyicileri
GOREV_BITTI_TETIK = ("GOREV_BITTI", "görev bitti", "tamamlandi", "TASK_DONE")


def tool_calls_al(yanit: dict) -> List[dict]:
    """Yanit dict'inden tool call'lari cikar.

    Desteklenen formatlar:
      1. OpenAI standard: yanit["tool_calls"] -> list
      2. ReAct text: icerik icinde ARAC("param") pattern
    """
    if not yanit:
        return []

    if isinstance(yanit.get("tool_calls"), list):
        return yanit["tool_calls"]

    icerik = yanit.get("content", "") or ""
    if not icerik:
        return []

    if any(t.lower() in icerik.lower() for t in GOREV_BITTI_TETIK):
        return []

    m = re.search(r"\b([A-Z][A-Z_]{2,})\s*\(([^)]*)\)", icerik)
    if m:
        arac_adi = m.group(1)
        if arac_adi in ("DUSUN", "YARDIM_ISTE", "DUSUNCE"):
            return []
        parametre = m.group(2).strip("\"'").strip()
        return [
            {
                "id": f"tc_{arac_adi}_{uuid.uuid4().hex[:6]}",
                "name": arac_adi,
                "arguments": {"param": parametre},
            }
        ]
    return []


def yanit_icerigi_al(yanit: dict) -> str:
    """Yanit dict'inden metin icerigi cikar."""
    if not yanit:
        return ""
    return yanit.get("content") or ""


def yanit_temizle(metin: str) -> str:
    """DUSUN/EYLEM gibi ic dusunce bloklarini temizle, GOREV_BITTI icindeki metni cikar."""
    if not metin:
        return metin

    # 1. GOREV_BITTI("...") -> icindeki metni cikar
    import re as _re
    gorev_m = _re.search(r'GOREV_BITTI\s*\(\s*"([^"]*)"\s*\)', metin)
    if gorev_m:
        return gorev_m.group(1).strip()

    # 2. DUSUN/EYLEM bloklarini temizle
    satirlar = metin.split("\n")
    temiz = []
    atla = False
    for s in satirlar:
        if _re.match(r"^\s*DUSUN\s*[\-:]", s):
            atla = True
            continue
        if _re.match(r"^\s*EYLEM\s*[\-:]", s):
            atla = True
            continue
        if atla and s.strip() == "":
            continue
        if atla and not _re.match(r"^\s*(DUSUN|EYLEM)\s*[\-:]", s):
            atla = False
        if not atla:
            temiz.append(s)
    sonuc = "\n".join(temiz).strip()
    return sonuc
