# -*- coding: utf-8 -*-
"""Kimlik bilgisi kaliciligi.

Hermes agent/credential_persistence.py'den adapte.
"""
from __future__ import annotations
import json
from pathlib import Path

class CredentialStore:
    def __init__(self, yol=None):
        self.yol = yol or Path.cwd() / ".ReYMeN" / "credentials.json"
    def kaydet(self, anahtar, deger):
        import json
        veri = {}
        if self.yol.exists():
            veri = json.loads(self.yol.read_text())
        veri[anahtar] = deger
        self.yol.write_text(json.dumps(veri, indent=2))
    def oku(self, anahtar):
        if self.yol.exists():
            return json.loads(self.yol.read_text()).get(anahtar)
        return None
