# -*- coding: utf-8 -*-
"""
session_db.py â€” ReYMeN SessionDB / Oturum YÃ¶neticisi.

Session verilerini SQLite'den okur. Deneme sirasi:
  1. ~/AppData/Local/reymen/profiles/reymen/state.db
  2. .ReYMeN/state.db
  3. Proje kokundeki state.db
  Hicbiri yoksa -> bos liste / bos dict doner.

Kullanim:
    db = SessionDB()
    db.list_sessions()   # -> [{'session_id': ..., 'created_at': ..., 'message_count': ...}]
    db.get_session(id)   # -> {...} veya {}
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SessionDB:
    """SessionDB â€” SQLite tabanli oturum yoneticisi.

    Veritabani yolunu otomatik kesfeder:
      1. ~/AppData/Local/reymen/profiles/reymen/state.db
      2. .ReYMeN/state.db  (proje kokune gore)
      3. Proje kokundeki state.db
    Hicbiri yoksa tum metodlar bos sonuc doner.

    Attributes:
        db_yolu: Kesfedilen SQLite dosya yolu (None = bulunamadi).
    """

    def __init__(self, proje_koku: Optional[Path] = None) -> None:
        """SessionDB baslatir.

        Args:
            proje_koku: Proje kok dizini (varsayilan: reymen/core/ -> 3 ust).
        """
        self._proje_koku = proje_koku or Path(__file__).resolve().parent.parent.parent
        self.db_yolu: Optional[Path] = self._db_bul()

    # â”€â”€ Veritabani kesfi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _db_bul(self) -> Optional[Path]:
        """state.db dosyasini sirasiyla ara.

        Returns:
            Bulunan Path veya None.
        """
        adaylar = [
            # 1. ReYMeN profil state.db
            Path.home()
            / "AppData"
            / "Local"
            / "reymen"
            / "profiles"
            / "reymen"
            / "state.db",
            # 2. .ReYMeN/state.db
            self._proje_koku / ".ReYMeN" / "state.db",
            # 3. Proje kokundeki state.db
            self._proje_koku / "state.db",
        ]

        for aday in adaylar:
            if aday.exists():
                logger.info("[SessionDB] state.db bulundu: %s", aday)
                return aday

        logger.warning("[SessionDB] state.db bulunamadi. Hicbir aday mevcut degil.")
        return None

    # â”€â”€ Baglanti â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _baglan(self) -> Optional[sqlite3.Connection]:
        """SQLite baglantisi acar.

        Returns:
            sqlite3.Connection veya None (db bulunamadiysa).
        """
        if self.db_yolu is None:
            return None
        try:
            conn = sqlite3.connect(str(self.db_yolu))
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error("[SessionDB] Baglanti hatasi: %s - %s", self.db_yolu, e)
            return None

    # â”€â”€ Metodlar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def list_sessions(self) -> list[dict[str, Any]]:
        """Tum oturumlari listeler.

        Returns:
            Her oturum icin:
                {'session_id': str, 'created_at': str, 'message_count': int}
            state.db yoksa veya tablo bossa bos liste doner.
        """
        conn = self._baglan()
        if conn is None:
            return []

        try:
            cursor = conn.execute(
                "SELECT session_id, created_at, message_count "
                "FROM sessions ORDER BY created_at DESC"
            )
            rows = [dict(row) for row in cursor.fetchall()]
            return rows
        except sqlite3.OperationalError:
            # Tablo yoksa sessizce bos don
            return []
        except sqlite3.Error as e:
            logger.error("[SessionDB] list_sessions hatasi: %s", e)
            return []
        finally:
            try:
                conn.close()
            except sqlite3.Error:
                logger.warning("[fix_01_sessiz_except] Error")

    def get_session(self, session_id: str) -> dict[str, Any]:
        """Tek bir oturumu getirir.

        Args:
            session_id: Aranan oturum kimligi.

        Returns:
            {'session_id': str, 'created_at': str, 'message_count': int}
            Bulunamazsa veya hata olursa bos dict {} doner.
        """
        conn = self._baglan()
        if conn is None:
            return {}

        try:
            cursor = conn.execute(
                "SELECT session_id, created_at, message_count "
                "FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return {}
            return dict(row)
        except sqlite3.OperationalError:
            return {}
        except sqlite3.Error as e:
            logger.error("[SessionDB] get_session hatasi: %s", e)
            return {}
        finally:
            try:
                conn.close()
            except sqlite3.Error:
                logger.warning("[fix_01_sessiz_except] Error")
