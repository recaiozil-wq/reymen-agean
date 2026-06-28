#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent/approval.py — ReYMeN Komut Onay Sistemi.

ReYMeN'teki command approval mekanizmasının ReYMeN uyarlaması.
Tehlikeli komutlari tespit eder, kullanici onayi ister.
"""

import re
from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.approval")

# ── Tehlikeli Komut Desenleri ────────────────────────────────────

DANGEROUS_PATTERNS: list[tuple[str, str, str]] = [
    # (desen, aciklama, regex)
    (r"rm\s+(-rf|--recursive|/*)", "recursive delete", "Dosya sistemi silme"),
    (r"mkfs\.\w+", "format disk", "Disk formatlama"),
    (r"dd\s+if=.*of=.*dev", "disk overwrite", "Diske dogrudan yazma"),
    (r"chmod\s+(777|666|a\+w|o\+w)", "world writable", "Herkes icin yazma izni"),
    (r"DROP\s+TABLE|DELETE\s+FROM\s+\w+\s+WHERE\s*$", "sql destructive", "SQL veri silme"),
    (r"systemctl\s+(stop|restart|disable)\s+", "service control", "Servis durdurma"),
    (r"curl\s+.*\|\s*(bash|sh)", "remote execution", "Uzaktan kod calistirma"),
    (r">\s*/etc/", "system config", "Sistem ayarlarini degistirme"),
    (r">\s*~/.ssh/", "ssh overwrite", "SSH anahtarlarini degistirme"),
    (r"pkill|killall\s+(hermes|reymen|gateway)", "self termination", "Kendini sonlandirma"),
]

# Her zaman engellenecek komutlar (hardline blocklist)
HARDLINE_BLOCKLIST: list[tuple[str, str]] = [
    (r"rm\s+-rf\s+/\s*$", "root silme"),
    (r":\(\)\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"mkfs\.\w+.*/dev/sd", "disk format"),
    (r"dd\s+if=/dev/zero\s+of=/dev/sd", "disk overwrite"),
]


class ApprovalManager:
    """Komut onay yoneticisi.

    Tehlikeli komutlari tespit eder, kullanici onayi mekanizmasi.
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}
        app_cfg = (self._config.get("approvals") or {})

        self._mode = app_cfg.get("mode", "smart")  # manual, smart, off
        self._timeout = app_cfg.get("timeout", 60)
        self._yolo = False
        self._allowlist: list[str] = app_cfg.get("command_allowlist", [])

        logger.info(f"ApprovalManager: mode={self._mode}, timeout={self._timeout}s")

    @property
    def yolo(self) -> bool:
        return self._yolo

    def yolo_ac(self):
        """YOLO modunu ac (tum onaylari atla)."""
        self._yolo = True
        logger.warning("YOLO mode ACTIVE - all approvals bypassed")

    def yolo_kapat(self):
        """YOLO modunu kapat."""
        self._yolo = False
        logger.info("YOLO mode disabled")

    def komut_kontrol(self, komut: str) -> dict:
        """Bir komutu guvenlik acisindan kontrol et.

        Args:
            komut: Calistirilacak komut

        Returns:
            dict: {
                "guvenli": bool,
                "engelle": bool,   # Hardline blocklist
                "onay_gerek": bool, # Kullanici onayi gerek
                "sebep": str,       # Aciklama
                "desen": str,       # Eslesen desen adi
            }
        """
        # Hardline blocklist (her zaman engelle)
        for pattern, aciklama in HARDLINE_BLOCKLIST:
            if re.search(pattern, komut, re.IGNORECASE):
                return {
                    "guvenli": False,
                    "engelle": True,
                    "onay_gerek": False,
                    "sebep": f"HARDLINE: {aciklama}",
                    "desen": aciklama,
                }

        # YOLO modu => tum onaylari atla
        if self._yolo or self._mode == "off":
            return {"guvenli": True, "engelle": False, "onay_gerek": False, "sebep": ""}

        # Allowlist kontrolu
        for izin in self._allowlist:
            if izin in komut:
                return {"guvenli": True, "engelle": False, "onay_gerek": False, "sebep": ""}

        # Tehlikeli desen kontrolu
        for pattern, ad, aciklama in DANGEROUS_PATTERNS:
            if re.search(pattern, komut, re.IGNORECASE):
                if self._mode == "smart":
                    # Smart mod: kisa komutlar otomatik onaylanabilir
                    if len(komut) < 30:
                        return {"guvenli": True, "engelle": False, "onay_gerek": False, "sebep": ""}

                return {
                    "guvenli": False,
                    "engelle": False,
                    "onay_gerek": True,
                    "sebep": f"Tehlikeli komut: {aciklama} ({ad})",
                    "desen": ad,
                }

        return {"guvenli": True, "engelle": False, "onay_gerek": False, "sebep": ""}

    def komut_islem(self, args: str = "") -> str:
        """/approval komutunu isle.

        Kullanim:
          /approval             -> Durum
          /approval yolo        -> YOLO modunu ac
          /approval safe        -> YOLO modunu kapat
          /approval mode smart  -> Mod degistir
        """
        if not args or args.lower() in ("status", "durum", ""):
            return (
                f"Onay Sistemi:\n"
                f"  Mod: {self._mode}\n"
                f"  YOLO: {'AKTIF ⚠️' if self._yolo else 'kapali'}\n"
                f"  Timeout: {self._timeout}s\n"
                f"  Allowlist: {len(self._allowlist)} kural\n"
                f"\n"
                f"Komutlar:\n"
                f"  /approval yolo      -> Tum onaylari gec\n"
                f"  /approval safe      -> Onaylari geri ac\n"
                f"  /approval mode <m>  -> smart|manual|off"
            )

        parts = args.strip().split(maxsplit=1)
        alt = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if alt == "yolo":
            self.yolo_ac()
            return "⚠️ YOLO MODU AKTIF — tum guvenlik onaylari pasif!"

        if alt == "safe":
            self.yolo_kapat()
            return "✅ Guvenlik onaylari geri aktif."

        if alt == "mode" and arg in ("smart", "manual", "off"):
            self._mode = arg
            return f"✅ Onay modu: {arg}"

        return f"[Approval] Bilinmeyen komut: {alt}"

    def ping(self) -> bool:
        return True


# ── Singleton ─────────────────────────────────────────────────────

_approval_instance: Optional[ApprovalManager] = None


def approval_manager(config: Optional[dict] = None) -> ApprovalManager:
    global _approval_instance
    if _approval_instance is None:
        _approval_instance = ApprovalManager(config)
    return _approval_instance
