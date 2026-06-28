# -*- coding: utf-8 -*-
"""gateway/platform_registry.py — Platform Kayıt Defteri.

Tüm platformları otomatik bulma, kaydetme, durum kontrolü.
"""

import dataclasses
import importlib
import inspect
import os
import pkgutil
import threading
import time
from typing import Any, Callable, Optional
import logging
logger = logging.getLogger(__name__)


class PlatformEntry:
    """Platform eklenti kaydı — plugin'lerin platform_registry'e kaydolmak için kullandığı yapı.

    Bilinen alanlar:
        name: Platform adı (benzersiz, küçük harf, tire kabul edilir).
        label: İnsan dostu görüntüleme adı.
        adapter_factory: ``(config) -> AdapterInstance`` çağrılabiliri.
        check_fn: Platformun kullanıma hazır olup olmadığını döndüren fonksiyon.
        validate_config: Config doğrulama fonksiyonu.
        required_env: Zorunlu ortam değişkenleri listesi.
        source: Kaydın kaynağı — "builtin" | "plugin" | "user".

    Bilinmeyen anahtar kelime argümanları yok sayılır (ileriye dönük uyumluluk).
    """

    def __init__(
        self,
        name: str,
        label: str = "",
        adapter_factory: Optional[Callable] = None,
        check_fn: Optional[Callable] = None,
        validate_config: Optional[Callable] = None,
        required_env: Optional[list] = None,
        source: str = "plugin",
        **_extra,  # bilinmeyen alanları sessizce yut
    ):
        self.name = name
        self.label = label
        self.adapter_factory = adapter_factory
        self.check_fn = check_fn
        self.validate_config = validate_config
        self.required_env = required_env or []
        self.source = source
        # ek alanları da sakla (introspection için)
        for k, v in _extra.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return f"<PlatformEntry name={self.name!r} source={self.source!r}>"


class PlatformRegistry:
    """Platform kayıt defteri — platformları bul, kaydet, durum kontrolü."""

    def __init__(self):
        self._platformlar: dict[str, dict] = {}
        self._kilit = threading.Lock()

    # ── Platform Kaydı ─────────────────────────────────────────────────

    def kaydet(self, ad: str, sinif: type,
               aciklama: str = "", versiyon: str = "1.0.0"):
        """Bir platformu kaydet.

        Args:
            ad: Platform adı (benzersiz)
            sinif: Platform sınıfı
            aciklama: Platform açıklaması
            versiyon: Platform versiyonu
        """
        with self._kilit:
            self._platformlar[ad] = {
                "ad": ad,
                "sinif": sinif,
                "aciklama": aciklama,
                "versiyon": versiyon,
                "kayit_zamani": time.time(),
                "durum": "kayitli",
                "son_kontrol": 0.0,
                "ornek": None,  # instance referansı
            }

    def kayitli_mi(self, ad: str) -> bool:
        """Platform kayıtlı mı?"""
        with self._kilit:
            return ad in self._platformlar

    def kaldir(self, ad: str) -> bool:
        """Platform kaydını kaldır."""
        with self._kilit:
            return bool(self._platformlar.pop(ad, None))

    def platform_al(self, ad: str) -> Optional[dict]:
        """Platform bilgilerini döndür."""
        with self._kilit:
            info = self._platformlar.get(ad)
            if info:
                return {k: v for k, v in info.items()
                        if k != "sinif" and k != "ornek"}
            return None

    # ── Otomatik Bulma ─────────────────────────────────────────────────

    def otomatik_bul(self, paket_yolu: Optional[str] = None):
        """Platform modüllerini otomatik bul ve kaydet.

        Args:
            paket_yolu: Taranacak paket yolu (None = gateway/platforms)
        """
        if paket_yolu is None:
            paket_yolu = os.path.join(os.path.dirname(__file__), "platforms")

        if not os.path.isdir(paket_yolu):
            return

        for bulunan in os.listdir(paket_yolu):
            if bulunan.endswith(".py") and not bulunan.startswith("_") and not bulunan.startswith("."):
                modul_adi = bulunan[:-3]
                try:
                    self._modulu_kaydet(modul_adi, paket_yolu)
                except Exception:
                    logger.warning("[fix_01_sessiz_except] Exception")

    def _modulu_kaydet(self, modul_adi: str, paket_yolu: str):
        """Bir modülü tara ve içindeki platform sınıflarını kaydet."""
        import sys
        if paket_yolu not in sys.path:
            sys.path.insert(0, paket_yolu)

        try:
            modul = importlib.import_module(modul_adi)
        except ImportError:
            # Göreceli import dene
            try:
                modul = importlib.import_module(f"gateway.platforms.{modul_adi}")
            except ImportError:
                return

        for isim, uye in inspect.getmembers(modul, inspect.isclass):
            if isim.lower().endswith("gateway") or isim.lower().endswith("platform"):
                aciklama = (uye.__doc__ or "").strip().split("\n")[0] if uye.__doc__ else ""
                self.kaydet(modul_adi, uye, aciklama=aciklama)

    # ── Durum Kontrolü ─────────────────────────────────────────────────

    def durum_kontrol(self, ad: str) -> str:
        """Bir platformun canlılık durumunu kontrol et."""
        with self._kilit:
            info = self._platformlar.get(ad)
            if not info:
                return "bulunamadi"

            sinif = info["sinif"]
            ornek = info.get("ornek")

            try:
                if ornek and hasattr(ornek, "ping"):
                    sonuc = ornek.ping()
                    info["durum"] = "aktif" if sonuc else "cevapsiz"
                elif hasattr(sinif, "ping"):
                    sonuc = sinif.ping()
                    info["durum"] = "aktif" if sonuc else "cevapsiz"
                else:
                    info["durum"] = "kayitli"
                info["son_kontrol"] = time.time()
            except Exception:
                info["durum"] = "hata"
                info["son_kontrol"] = time.time()

            return info["durum"]

    def tum_durum(self) -> dict[str, str]:
        """Tüm platformların durumunu kontrol et."""
        with self._kilit:
            adlar = list(self._platformlar.keys())
        return {ad: self.durum_kontrol(ad) for ad in adlar}

    def ornek_ata(self, ad: str, ornek: Any):
        """Platform örneğini kaydet."""
        with self._kilit:
            if ad in self._platformlar:
                self._platformlar[ad]["ornek"] = ornek
                self._platformlar[ad]["durum"] = "aktif"

    def platform_listesi(self) -> list[dict]:
        """Tüm platformların özet listesi."""
        with self._kilit:
            return [
                {
                    "ad": v["ad"],
                    "aciklama": v["aciklama"],
                    "versiyon": v["versiyon"],
                    "durum": v["durum"],
                }
                for v in self._platformlar.values()
            ]

    def platform_ornegi(self, ad: str) -> Optional[Any]:
        """Platform örneğini döndür."""
        with self._kilit:
            info = self._platformlar.get(ad)
            return info.get("ornek") if info else None

    def register(self, entry: "PlatformEntry") -> None:
        """PlatformEntry nesnesiyle platform kaydet (plugin arayüzü)."""
        self.kaydet(
            ad=entry.name,
            sinif=type(entry.adapter_factory) if entry.adapter_factory else object,
            aciklama=entry.label,
        )

    def get(self, ad: str) -> Optional["PlatformEntry"]:
        """Platform kaydını PlatformEntry olarak döndür."""
        info = self.platform_al(ad)
        if info:
            return PlatformEntry(
                name=info["ad"],
                label=info.get("aciklama", ""),
                source=info.get("source", "builtin"),
            )
        return None

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "platform_registry",
            "durum": "hazir",
            "platform_sayisi": len(self._platformlar),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Bir platform üzerinden mesaj gönder."""
        platform = self.platform_ornegi(hedef)
        if platform and hasattr(platform, "send_message"):
            try:
                return platform.send_message(mesaj, **kwargs)
            except Exception as e:
                return f"[Registry]: {hedef} üzerinden gönderim hatası — {e}"
        return f"[Registry]: '{hedef}' platformu bulunamadı veya send_message yok."


# Global instance
kayit = PlatformRegistry()
platform_registry = kayit  # plugin'lerin beklediği isim


if __name__ == "__main__":
    pr = PlatformRegistry()
    print("Otomatik bulma deneniyor...")
    pr.otomatik_bul()
    print(f"Bulunan platformlar: {len(pr.platform_listesi())}")
    for p in pr.platform_listesi():
        print(f"  - {p['ad']}: {p['durum']}")
    print(pr.ping())
