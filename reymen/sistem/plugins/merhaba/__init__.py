# -*- coding: utf-8 -*-
"""
merhaba — ReYMeN örnek plugin'i.

Arayüz:
    plugin_adi      = "merhaba"
    plugin_aciklamasi = "ReYMeN örnek plugin"
    kaydet(motor)   → araçları motor'a kaydeder
"""

plugin_adi = "merhaba"
plugin_aciklamasi = "ReYMeN örnek plugin — HOT-RELOAD calisiyor!"
plugin_araclar = ["MERHABA_SOYLE", "PLUGIN_BILGI", "MERHABA_VERSIYON"]


def kaydet(motor):
    """Plugin araçlarını motor'a kaydet."""
    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "MERHABA_SOYLE",
            lambda ham: f"[Merhaba Plugin] Merhaba! Parametre: {ham.strip()!r}",
            "Örnek plugin mesajı döndürür",
        )
        motor._plugin_arac_kaydet(
            "PLUGIN_BILGI",
            lambda ham: (
                f"[Merhaba Plugin]\n"
                f"  Adı: {plugin_adi}\n"
                f"  Açıklama: {plugin_aciklamasi}\n"
                f"  Araçlar: {', '.join(plugin_araclar)}\n"
                f"  Sürüm: 1.0.0"
            ),
            "Plugin bilgilerini döndürür",
        )
        motor._plugin_arac_kaydet(
            "MERHABA_VERSIYON",
            lambda ham: "[Merhaba Plugin] Surum: 1.0.0 (hot-reload destekli)",
            "Plugin versiyonunu döndürür",
        )
        return True
    return False


def run(**kwargs):
    """PluginManager.run() uyumluluğu için."""
    target = kwargs.get("target", "")
    if target:
        return f"[Merhaba Plugin] Merhaba {target}!"
    return "[Merhaba Plugin] Merhaba Dünya!"


if __name__ == "__main__":
    print(run(target="ReYMeN"))
