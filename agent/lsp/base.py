"""
Temel LSP istemci soyut sınıfı.

Tüm dil sunucusu istemcilerinin uygulaması gereken arayüz.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class LSPClientBase(ABC):
    """Soyut LSP istemci temel sınıfı."""

    @abstractmethod
    def baslat(self) -> None:
        """LSP sunucusuna bağlantıyı başlatır."""
        ...

    @abstractmethod
    def durdur(self) -> None:
        """LSP sunucusu ile bağlantıyı kapatır."""
        ...

    @abstractmethod
    def tamamlama_istek(self, metin: str) -> list[dict[str, Any]]:
        """Otomatik tamamlama isteği gönderir.

        Args:
            metin: Tamamlama yapılacak metin.

        Returns:
            Tamamlama önerileri listesi.
        """
        ...

    @abstractmethod
    def tanim_istek(self, dosya: str, satir: int, sutun: int) -> Optional[dict[str, Any]]:
        """Tanıma git (go to definition) isteği gönderir.

        Args:
            dosya: Dosya yolu.
            satir: Satır numarası (0-indexed).
            sutun: Sütun numarası (0-indexed).

        Returns:
            Tanım konumu bilgisi veya None.
        """
        ...

    def run(self, **kwargs) -> str:
        """Varsayılan çalıştırma metodu (alt sınıflar override edebilir).

        Returns:
            İşlem sonucu metni.
        """
        return "LSPClientBase: çalıştırıldı"
