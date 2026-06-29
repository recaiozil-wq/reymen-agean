# -*- coding: utf-8 -*-
"""
merhaba — ReYMeN örnek plugin'i.

Arayüz:
    plugin_adi          = "merhaba"
    plugin_aciklamasi   = "ReYMeN örnek plugin"
    plugin_providers    = ["varsayilan", "gelismis"]
    kaydet(motor)       → araçları motor'a kaydeder

Provider desteği:
    Plugin başlatılırken `_aktif_provider` attribute'u set edilir.
    Bu attribute plugin'in hangi provider ile çalıştığını belirtir.
    Provider bilgisi plugin.yaml'deki `providers` listesinden gelir.
"""

import logging

logger = logging.getLogger(__name__)

plugin_adi = "merhaba"
plugin_aciklamasi = "ReYMeN örnek plugin — HOT-RELOAD ve PROVIDER destekli!"
plugin_araclar = ["MERHABA_SOYLE", "PLUGIN_BILGI", "MERHABA_VERSIYON"]
plugin_providers = ["varsayilan", "gelismis"]  # runtime erişim için


# ── ProviderPluginBase alt sinifi ─────────────────────────────────────────
try:
    from reymen.sistem.provider_plugin_base import ProviderPluginBase

    class MerhabaProvider(ProviderPluginBase):
        """Merhaba plugin'i icin provider yoneticisi."""

        name = "merhaba_provider"
        version = "1.0.0"

        def init(self, config: dict | None = None) -> bool:
            """Provider'i baslat."""
            logger.info("[MerhabaProvider] Baslatildi (config: %s)", config)
            return True

        def health_check(self) -> dict:
            """Saglik kontrolu."""
            return {
                "status": "ok",
                "latency_ms": 0,
                "message": f"MerhabaProvider aktif, provider: {self._active_provider}",
            }

        def shutdown(self) -> None:
            """Provider'i kapat."""
            logger.info("[MerhabaProvider] Kapatildi.")

except ImportError:
    # ProviderPluginBase yoksa sorunsuz devam et
    MerhabaProvider = None  # type: ignore


def _aktif_provider_al() -> str:
    """Plugin'in aktif provider'ını döndür (varsayılan: 'varsayilan')."""
    import sys
    mod = sys.modules.get(__name__)
    if mod is None:
        return "varsayilan"
    return getattr(mod, "_aktif_provider", "varsayilan") or "varsayilan"


def _provider_mesaj(ham: str, provider: str) -> str:
    """Provider'a göre mesaj üret."""
    if provider == "gelismis":
        return (
            f"[Merhaba Plugin :: gelismis]\n"
            f"  ✦ Merhaba! (gelişmiş provider)\n"
            f"  ✦ Parametre: {ham.strip()!r}\n"
            f"  ✦ Zaman damgası eklendi\n"
            f"  ✦ Emoji desteği: 🎉✨🚀"
        )
    # varsayilan / fallback
    return f"[Merhaba Plugin :: varsayilan] Merhaba! Parametre: {ham.strip()!r}"


def kaydet(motor):
    """Plugin araçlarını motor'a kaydet.

    Provider bilgisi modülün _aktif_provider attribute'undan okunur.
    Eğer set edilmemişse (örneğin plugin hot-reload edildiyse)
    varsayılan provider kullanılır.
    """
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "MERHABA_SOYLE",
            lambda ham: _provider_mesaj(ham, _aktif_provider_al()),
            "Örnek plugin mesajı döndürür (provider'a göre değişir)",
        )
        motor._plugin_arac_kaydet(
            "PLUGIN_BILGI",
            lambda ham: (
                f"[Merhaba Plugin]\n"
                f"  Adı: {plugin_adi}\n"
                f"  Açıklama: {plugin_aciklamasi}\n"
                f"  Araçlar: {', '.join(plugin_araclar)}\n"
                f"  Sürüm: 1.0.0\n"
                f"  Aktif Provider: {_aktif_provider_al()}\n"
                f"  Desteklenen Provider'lar: {', '.join(plugin_providers)}"
            ),
            "Plugin bilgilerini döndürür",
        )
        motor._plugin_arac_kaydet(
            "MERHABA_VERSIYON",
            lambda ham: (
                f"[Merhaba Plugin] Surum: 1.0.0 "
                f"(hot-reload + provider destekli, aktif provider: {_aktif_provider_al()})"
            ),
            "Plugin versiyonunu döndürür",
        )
        return True
    return False


def run(**kwargs):
    """PluginManager.run() uyumluluğu için."""
    target = kwargs.get("target", "")
    provider = _aktif_provider_al()
    if target:
        return _provider_mesaj(target, provider)
    return _provider_mesaj("Dünya", provider)


if __name__ == "__main__":
    print(run(target="ReYMeN"))
