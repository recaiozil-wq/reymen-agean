# -*- coding: utf-8 -*-
"""acp_adapter/session.py — ACP oturum yoneticisi."""
import threading
from datetime import datetime, timezone


class SessionYoneticisi:
    """ACP oturum yöneticisi."""

    def __init__(self):
        self._oturumlar: dict[str, dict] = {}
        self._kilit = threading.Lock()

    def oturum_ac(self, session_id: str, hedef: str) -> dict:
        oturum = {
            "session_id": session_id,
            "hedef": hedef,
            "durum": "bekliyor",
            "sonuc": "",
            "baslangi": datetime.now(timezone.utc).isoformat(),
            "bitis": "",
        }
        with self._kilit:
            self._oturumlar[session_id] = oturum
        return oturum

    def durum_guncelle(self, session_id: str, durum: str, sonuc: str = ""):
        with self._kilit:
            if session_id in self._oturumlar:
                self._oturumlar[session_id]["durum"] = durum
                if sonuc:
                    self._oturumlar[session_id]["sonuc"] = sonuc
                if durum in ("tamamlandi", "hata"):
                    self._oturumlar[session_id]["bitis"] = datetime.now(timezone.utc).isoformat()

    def oturum_bul(self, session_id: str) -> dict | None:
        with self._kilit:
            return self._oturumlar.get(session_id)

    def tum_oturumlar(self) -> list[dict]:
        with self._kilit:
            return list(self._oturumlar.values())


SessionManager = SessionYoneticisi  # alias for test compatibility
