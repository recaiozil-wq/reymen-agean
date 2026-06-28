# -*- coding: utf-8 -*-
"""gateway/display_config.py — Görüntüleme Ayarları.

Platforma göre mesaj formatı, maksimum uzunluk, markdown/HTML dönüşümü.
"""

import re
from typing import Optional, Any


class DisplayConfig:
    """Görüntüleme yapılandırması — platform bazlı format ve dönüşüm."""

    def __init__(self):
        # Varsayılan platform yapılandırmaları
        self._platformlar: dict[str, dict] = {
            "telegram": {
                "max_uzunluk": 4096,
                "format": "markdown",
                "link_previzyonu": True,
                "emojii_destegi": True,
                "kod_blok": True,
            },
            "whatsapp": {
                "max_uzunluk": 4096,
                "format": "plain",
                "link_previzyonu": True,
                "emojii_destegi": True,
                "kod_blok": False,
            },
            "sms": {
                "max_uzunluk": 1600,
                "format": "plain",
                "link_previzyonu": False,
                "emojii_destegi": False,
                "kod_blok": False,
            },
            "discord": {
                "max_uzunluk": 2000,
                "format": "markdown",
                "link_previzyonu": True,
                "emojii_destegi": True,
                "kod_blok": True,
            },
            "slack": {
                "max_uzunluk": 40000,
                "format": "markdown",
                "link_previzyonu": True,
                "emojii_destegi": True,
                "kod_blok": True,
            },
            "matrix": {
                "max_uzunluk": 65536,
                "format": "html",
                "link_previzyonu": True,
                "emojii_destegi": True,
                "kod_blok": True,
            },
            "wecom": {
                "max_uzunluk": 2048,
                "format": "markdown",
                "link_previzyonu": False,
                "emojii_destegi": False,
                "kod_blok": False,
            },
            "default": {
                "max_uzunluk": 4096,
                "format": "plain",
                "link_previzyonu": True,
                "emojii_destegi": True,
                "kod_blok": False,
            },
        }

    # ── Platform Yapılandırması ────────────────────────────────────────

    def platform_ekle(self, platform: str, ayarlar: dict):
        """Yeni platform görüntüleme ayarı ekle."""
        self._platformlar[platform] = {
            "max_uzunluk": ayarlar.get("max_uzunluk", 4096),
            "format": ayarlar.get("format", "plain"),
            "link_previzyonu": ayarlar.get("link_previzyonu", True),
            "emojii_destegi": ayarlar.get("emojii_destegi", True),
            "kod_blok": ayarlar.get("kod_blok", False),
        }

    def platform_ayari(self, platform: str) -> dict:
        """Platformun görüntüleme ayarlarını döndür."""
        return dict(self._platformlar.get(platform, self._platformlar["default"]))

    def max_uzunluk(self, platform: str) -> int:
        """Platform için maksimum mesaj uzunluğu."""
        return self.platform_ayari(platform)["max_uzunluk"]

    # ── Format Dönüşüm ─────────────────────────────────────────────────

    def bicimle(self, platform: str, mesaj: str) -> str:
        """Mesajı platformun formatına göre biçimlendir.

        Args:
            platform: Hedef platform
            mesaj: Ham mesaj

        Returns:
            Platforma uygun biçimlenmiş mesaj
        """
        ayar = self.platform_ayari(platform)
        max_len = ayar["max_uzunluk"]

        # Markdown -> HTML dönüşümü (eğer platform HTML bekliyorsa)
        if ayar["format"] == "html" and not self._html_mi(mesaj):
            mesaj = self._markdown_to_html(mesaj)

        # HTML -> Plain dönüşümü (eğer platform düz metin bekliyorsa)
        if ayar["format"] == "plain":
            mesaj = self._html_to_plain(mesaj)
            mesaj = self._markdown_temizle(mesaj)

        # Kod blokları kontrolü
        if not ayar["kod_blok"]:
            mesaj = self._kod_blok_temizle(mesaj)

        # Link previzyonu kontrolü
        if not ayar["link_previzyonu"]:
            mesaj = self._link_engelle(mesaj)

        # Maksimum uzunluk
        if len(mesaj) > max_len:
            mesaj = mesaj[: max_len - 3] + "..."

        return mesaj

    # ── Dönüşüm Yardımcıları ──────────────────────────────────────────

    @staticmethod
    def _html_mi(metin: str) -> bool:
        return bool(re.search(r"<[a-z][\s\S]*>", metin, re.I))

    @staticmethod
    def _markdown_to_html(metin: str) -> str:
        """Basit markdown -> HTML dönüşümü."""
        metin = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", metin)
        metin = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", metin)
        metin = re.sub(r"\*(.+?)\*", r"<em>\1</em>", metin)
        metin = re.sub(r"`(.+?)`", r"<code>\1</code>", metin)
        metin = re.sub(r"```(\w*)\n([\s\S]*?)```", r"<pre><code>\2</code></pre>", metin)
        metin = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', metin)
        metin = re.sub(r"^### (.+)$", r"<h3>\1</h3>", metin, flags=re.M)
        metin = re.sub(r"^## (.+)$", r"<h2>\1</h2>", metin, flags=re.M)
        metin = re.sub(r"^# (.+)$", r"<h1>\1</h1>", metin, flags=re.M)
        return metin

    @staticmethod
    def _html_to_plain(metin: str) -> str:
        """HTML -> düz metin dönüşümü."""
        metin = re.sub(r"<br\s*/?>", "\n", metin)
        metin = re.sub(r"<[^>]+>", "", metin)
        metin = re.sub(r"&amp;", "&", metin)
        metin = re.sub(r"&lt;", "<", metin)
        metin = re.sub(r"&gt;", ">", metin)
        return metin

    @staticmethod
    def _markdown_temizle(metin: str) -> str:
        """Markdown biçimlendirmesini temizle, sadece metin bırak."""
        metin = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", metin)
        metin = re.sub(r"\*\*(.+?)\*\*", r"\1", metin)
        metin = re.sub(r"\*(.+?)\*", r"\1", metin)
        metin = re.sub(r"`(.+?)`", r"\1", metin)
        metin = re.sub(r"```[\s\S]*?```", "", metin)
        metin = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", metin)
        return metin

    @staticmethod
    def _kod_blok_temizle(metin: str) -> str:
        """Kod bloklarını metinden çıkar."""
        metin = re.sub(r"```[\s\S]*?```", "[kod blogu]", metin)
        metin = re.sub(r"`([^`]+)`", r"\1", metin)
        return metin

    @staticmethod
    def _link_engelle(metin: str) -> str:
        """Link previzyonunu engelle (URL'leri gizle)."""
        metin = re.sub(
            r"https?://[^\s<>\"']+",
            "[link]",
            metin,
        )
        return metin

    # ── Ortak Gateway Metodları ────────────────────────────────────────

    def ping(self) -> dict:
        """Sağlık kontrolü."""
        return {
            "modul": "display_config",
            "durum": "hazir",
            "platform_sayisi": len(self._platformlar),
        }

    def send_message(self, mesaj: str, hedef: str, **kwargs) -> str:
        """Mesajı platforma göre biçimlendir ve döndür."""
        bicimli = self.bicimle(hedef, mesaj)
        return f"[Display] {hedef}: {bicimli[:80]}..."


def resolve_display_setting(platform: str, setting: str, default: Any = None) -> Any:
    """Platform icin gosterim ayarini coz.

    Upstream Hermes uyumluluk fonksiyonu.

    Args:
        platform: Platform adi (ornek: \"telegram\", \"discord\")
        setting: Ayar anahtari (ornek: \"max_uzunluk\", \"format\")
        default: Varsayilan deger

    Returns:
        Ayar degeri veya varsayilan
    """
    try:
        return goruntu.platform_ayari(platform).get(setting, default)
    except Exception:
        return default


# Global instance
goruntu = DisplayConfig()


if __name__ == "__main__":
    dc = DisplayConfig()
    mesaj = "**Kalın** ve *italik* ve `kod`"
    print(f"Telegram: {dc.bicimle('telegram', mesaj)}")
    print(f"SMS: {dc.bicimle('sms', mesaj)}")
    print(f"Matrix (HTML): {dc.bicimle('matrix', mesaj)}")
    print(dc.ping())
