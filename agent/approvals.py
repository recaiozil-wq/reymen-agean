#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent/approvals.py — ReYMeN Komut Onay Sistemi.

ReYMeN'teki approvals sisteminin ReYMeN uyarlamasi:
- Tehlikeli komut onayi (manual/smart/off)
- Hardline blocklist (her zaman engellenen komutlar)
- Allowlist (her zaman izin verilen komutlar)
- Konsol ve mesajlasma arayuzu
"""

import os
import re
from pathlib import Path
from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.approvals")


# ── Hardline Blocklist (Her Zaman Engellenen) ───────────────────

HARDLINE_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+-rf\s+/\s*$", "root silmeye calisiyor"),          # sadece / (root)
    (r"rm\s+-rf\s+/(?:bin|boot|etc|lib|proc|root|sbin|sys|usr|var)\b", "sistem dizini silme"),
    (r"mkfs\s+.*/dev/sd", "disk formatlama"),
    (r"dd\s+if=.*of=/dev/sd", "diske dogrudan yazma"),
    (r":\(\)\s*\{.*:\|:&\s*\}\s*;", "fork bomb"),
    (r"curl\s+\S+\s*\|\s*(sudo\s+)?(bash|sh)", "curl'den bash'a RCE"),
    (r"wget\s+\S+\s*-O\s*-\s*\|\s*(sudo\s+)?(bash|sh)", "wget'ten bash'a RCE"),
    (r"chmod\s+777\s+/\s*$", "kok dizine 777"),
    (r">\s*/dev/sd", "diske yonlendirme"),
    (r"kill\s+-9\s+-1", "tum prosesleri oldur"),
]

# ── Tehlikeli Komut Desenleri (Onay Gerektiren) ────────────────

TEHLIKELI_PATTERNS: list[tuple[str, str]] = [
    (r"rm\s+-(rf|r)\s+", "rekursif silme"),
    (r"chmod\s+(777|666|a=rwx)", "acik izin"),
    (r"chown\s+.*root:", "root sahipligi"),
    (r"systemctl\s+(stop|restart|disable|mask)", "sistem servisi durdurma"),
    (r"DROP\s+(TABLE|DATABASE)", "SQL tablo/silme"),
    (r"DELETE\s+FROM\s+\w+\s+(?!.*WHERE)", "SQL WHERE'siz silme"),
    (r"TRUNCATE\s+", "SQL tablo temizleme"),
    (r">\s*/etc/", "etc dizinine yazma"),
    (r"sudo\s+", "sudo komutu"),
    (r"pip\s+uninstall", "paket kaldirma"),
    (r"apt\s+(remove|purge|autoremove)", "paket silme"),
    (r"docker\s+(rm|rmi|system\s+prune)", "docker temizlik"),
    (r"find\s+.*-delete", "find ile silme"),
    (r"sed\s+-i\s+.*/etc/", "sed ile etc duzenleme"),
]


class ApprovalManager:
    """Komut onay yoneticisi.

    Modlar:
      manual: Her tehlikeli komutta kullaniciya sor
      smart:  Dusuk riskli => otomatik onay, yuksek => sor
      off:    Tum onaylari gec (CI/CD icin)
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}
        app_cfg = (self._config.get("approvals") or {})

        self._mod = app_cfg.get("mode", "manual")  # manual | smart | off
        self._timeout = app_cfg.get("timeout", 60)
        self._yolo = False

        # Allowlist
        self._allowlist: list[str] = app_cfg.get("allowlist", [])

        logger.info(f"ApprovalManager: mode={self._mod}, timeout={self._timeout}s")

    # ── Komut Kontrol ──────────────────────────────────────────

    def komut_kontrol(self, komut: str) -> dict:
        """Bir komutu guvenlik katmanlarindan gecir.

        Returns:
            {"durum": "izin"|"engel"|"onay",
             "sebep": str,
             "onem": str}
        """
        # 1) Allowlist — kullanici daha önce "her_zaman" dedi
        for izinli in self._allowlist:
            if izinli.lower() in komut.lower():
                return {"durum": "izin", "sebep": "allowlist", "onem": "dusuk"}

        # 2) YOLO / off modu — hardline'dan önce: kullanici bilinçli seçim yaptı
        if self._yolo or self._mod == "off":
            return {"durum": "izin", "sebep": "yolo/off", "onem": "dusuk"}

        # 3) Hardline blocklist — hiçbir onay mekanizmasıyla geçilemeyen mutlak engel
        for pattern, aciklama in HARDLINE_PATTERNS:
            if re.search(pattern, komut, re.IGNORECASE):
                return {
                    "durum": "engel",
                    "sebep": f"HARDLINE: {aciklama}",
                    "onem": "kritik",
                }

        # 4) Tehlikeli desen kontrolu
        for pattern, aciklama in TEHLIKELI_PATTERNS:
            if re.search(pattern, komut, re.IGNORECASE):
                if self._mod == "smart":
                    # Smart: kisa komutlar dusuk risk
                    if len(komut.split()) <= 3:
                        return {
                            "durum": "izin",
                            "sebep": f"smart: {aciklama} (kisa komut)",
                            "onem": "dusuk",
                        }
                return {
                    "durum": "onay",
                    "sebep": aciklama,
                    "onem": "orta",
                }

        return {"durum": "izin", "sebep": "guvenli", "onem": "dusuk"}

    def onayla(self, komut: str, kullanici_cevabi: str = "") -> dict:
        """Kullanici cevabina gore komutu onayla/reddet.

        Args:
            komut: Calistirilacak komut
            kullanici_cevabi: "evet"/"hayir"/"her_zaman"/""

        Returns:
            {"durum": "izin"|"engel", "sebep": str}
        """
        kontrol = self.komut_kontrol(komut)

        if kontrol["durum"] == "engel":
            return {"durum": "engel", "sebep": kontrol["sebep"]}

        if kontrol["durum"] == "izin":
            return {"durum": "izin", "sebep": kontrol["sebep"]}

        # Onay gerekiyor
        cevap = kullanici_cevabi.lower().strip() if kullanici_cevabi else ""

        if cevap in ("evet", "e", "yes", "y", "ok", "approve"):
            return {"durum": "izin", "sebep": "kullanici onayi"}
        if cevap in ("her_zaman", "always", "a"):
            self._allowlist.append(komut.split()[0])
            return {"durum": "izin", "sebep": "allowlist eklendi"}
        if cevap in ("hayir", "h", "no", "n", "deny"):
            return {"durum": "engel", "sebep": "kullanici reddetti"}

        # Cevap yoksa onay bekliyor
        return {"durum": "bekliyor", "sebep": kontrol["sebep"], "komut": komut}

    # ── /approvals Slash Komutu ─────────────────────────────────

    def komut_islem(self, args: str = "") -> str:
        """/approvals komutu.

        Kullanim:
          /approvals              -> Durum
          /approvals mode manual  -> Mod degistir
          /approvals yolo         -> YOLO toggle
          /approvals allowlist    -> Allowlist goster
          /approvals test <komut> -> Komut test et
        """
        if not args or args.lower() in ("durum", "status", ""):
            return self._durum_goster()

        parts = args.strip().split(maxsplit=1)
        alt = parts[0].lower()
        alt_args = parts[1] if len(parts) > 1 else ""

        if alt == "mode":
            if alt_args in ("manual", "smart", "off"):
                self._mod = alt_args
                return f"[Approval] Mod: {alt_args}"
            return f"[Approval] Gecersiz mod: {alt_args} (manual|smart|off)"

        if alt == "yolo":
            self._yolo = not self._yolo
            return f"[Approval] YOLO: {'AKTIF' if self._yolo else 'PASIF'}"

        if alt == "allowlist":
            if not self._allowlist:
                return "[Approval] Allowlist bos."
            return "[Approval] Allowlist:\n  " + "\n  ".join(self._allowlist)

        if alt == "test":
            if not alt_args:
                return "[Approval] Kullanim: /approvals test <komut>"
            r = self.komut_kontrol(alt_args)
            return f"[Approval] Test: '{alt_args[:60]}' => {r['durum']} ({r['sebep']})"

        return f"[Approval] Bilinmeyen: {alt}"

    def _durum_goster(self) -> str:
        return (
            "ReYMeN Guvenlik Sistemi\n"
            f"  Mod: {self._mod}\n"
            f"  YOLO: {'AKTIF ⚠️' if self._yolo else 'pasif'}\n"
            f"  Timeout: {self._timeout}s\n"
            f"  Allowlist: {len(self._allowlist)} kayit\n"
            f"  Hardline: {len(HARDLINE_PATTERNS)} desen\n"
            "\n"
            "Komutlar:\n"
            "  /approvals                    -> Durum\n"
            "  /approvals mode <manual|smart|off>\n"
            "  /approvals yolo               -> YOLO toggle\n"
            "  /approvals allowlist          -> Liste\n"
            "  /approvals test <komut>       -> Test\n"
        )

    def ping(self) -> bool:
        return True


# ── Singleton ─────────────────────────────────────────────────────

_approval_instance: Optional[ApprovalManager] = None


def approval_manager(config: Optional[dict] = None) -> ApprovalManager:
    global _approval_instance
    if _approval_instance is None:
        _approval_instance = ApprovalManager(config)
    return _approval_instance
