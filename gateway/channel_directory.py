# -*- coding: utf-8 -*-
"""gateway/channel_directory.py — Kanal Dizini.

Hangi kanalın hangi platforma ait olduğunu, alias mapping'i yönetir.
JSON tabanlı depolama.
"""

import json
import os
import threading
from typing import Optional
import logging
logger = logging.getLogger(__name__)


CHANNEL_DIR_PATH = os.environ.get(
    "CHANNEL_DIR_PATH",
    os.path.join(os.path.dirname(__file__), "channel_directory.json"),
)


class ChannelDirectory:
    """Kanal dizini — kanal-platform eşlemesi ve alias yönetimi."""

    def __init__(self, json_path: str = CHANNEL_DIR_PATH):
        self._json_path = json_path
        self._kilit = threading.Lock()
        self._kanallar: dict[str, dict] = {}  # kanal_id -> {platform, alias, meta}
        self._alias_map: dict[str, str] = {}  # alias -> kanal_id
        self._yukle()

    # ── JSON Depolama ──────────────────────────────────────────────────

    def _yukle(self):
        """JSON dosyasından kanalları yükle."""
        try:
            if os.path.exists(self._json_path):
                with open(self._json_path, "r", encoding="utf-8") as f:
                    veri = json.load(f)
                self._kanallar = veri.get("kanallar", {})
                self._alias_map = veri.get("alias_map", {})
        except (json.JSONDecodeError, OSError):
            self._kanallar = {}
            self._alias_map = {}

    def _kaydet(self):
        """Kanalları JSON dosyasına yaz."""
        try:
            with open(self._json_path, "w", encoding="utf-8") as f:
                json.dump(
                    {"kanallar": self._kanallar, "alias_map": self._alias_map},
                    f, indent=2, ensure_ascii=False,
                )
        except OSError as e:
            raise RuntimeError(f"Kanal dizini kaydedilemedi: {e}")

    # ── Kanal Yönetimi ─────────────────────────────────────────────────

    def kanal_ekle(self, kanal_id: str, platform: str, alias: str = "",
                   meta: Optional[dict] = None):
        """Yeni kanal kaydet.

        Args:
            kanal_id: Benzersiz kanal kimliği
            platform: Platform adı (telegram, whatsapp, vs.)
            alias: Opsiyonel takma ad
            meta: Ek metadata
        """
        with self._kilit:
            self._kanallar[kanal_id] = {
                "platform": platform,
                "alias": alias or kanal_id,
                "meta": meta or {},
            }
            if alias:
                self._alias_map[alias] = kanal_id
            self._kaydet()

    def kanal_sil(self, kanal_id: str) -> bool:
        """Kanal sil."""
        with self._kilit:
            kanal = self._kanallar.pop(kanal_id, None)
            if kanal:
                alias = kanal.get("alias")
                if alias and alias in self._alias_map:
                    del self._alias_map[alias]
                self._kaydet()
                return True
            return False

    def kanal_bul(self, sorgu: str) -> Optional[dict]:
        """Kanal ID veya alias ile kanal bul."""
        with self._kilit:
            # Önce direkt ID ara
            if sorgu in self._kanallar:
                return {**self._kanallar[sorgu], "id": sorgu}
            # Alias üzerinden ara
            kanal_id = self._alias_map.get(sorgu)
            if kanal_id and kanal_id in self._kanallar:
                return {**self._kanallar[kanal_id], "id": kanal_id}
            return None

    def platform_kanallari(self, platform: str) -> list[dict]:
        """Belirli bir platformdaki tüm kanalları döndür."""
        with self._kilit:
            return [
                {**v, "id": k}
                for k, v in self._kanallar.items()
                if v["platform"] == platform
            ]

    def tum_kanallar(self) -> list[dict]:
        """Tüm kanalları listele."""
        with self._kilit:
            return [{**v, "id": k} for k, v in self._kanallar.items()]

    def alias_ekle(self, kanal_id: str, alias: str) -> bool:
        """Mevcut bir kanala alias ekle."""
        with self._kilit:
            if kanal_id not in self._kanallar:
                return False
            if alias in self._alias_map:
                return False
            self._kanallar[kanal_id]["alias"] = alias
            self._alias_map[alias] = kanal_id
            self._kaydet()
            return True

    def kanal_sayisi(self) -> int:
        """Toplam kanal sayısı."""
        with self._kilit:
            return len(self._kanallar)

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "channel_directory",
            "durum": "hazir",
            "kanal_sayisi": self.kanal_sayisi(),
            "alias_sayisi": len(self._alias_map),
            "dosya": self._json_path,
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Kanal dizini üzerinden mesaj gönder (hedef kanal ID'si)."""
        kanal = self.kanal_bul(hedef)
        if not kanal:
            return f"[Kanal]: '{hedef}' bulunamadı."
        return f"[Kanal] {kanal['platform']}/{hedef}: {mesaj[:80]}"


# Global instance
dizin = ChannelDirectory()


if __name__ == "__main__":
    cd = ChannelDirectory()
    cd.kanal_ekle("test_channel", "telegram", alias="test")
    print(cd.tum_kanallar())
    print(cd.kanal_bul("test"))
    print(cd.ping())
