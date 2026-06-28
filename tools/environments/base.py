"""
tools.environments.base — Temel Environment Soyut Sınıfı

Tüm ortam backend'leri bu sınıftan türetilmelidir.
Türkçe docstring ile belgelenmiştir.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseEnvironment(ABC):
    """Tüm ortamlar için temel soyut sınıf.

    Her ortam backend'i şu metotları uygulamalıdır:
        - execute(): Komut çalıştırma
        - ping(): Bağlantı/kullanılabilirlik kontrolü
        - bilgi(): Ortam hakkında bilgi döndürme
    """

    @abstractmethod
    def execute(self, komut: str, timeout: Optional[int] = None) -> Any:
        """Belirtilen komutu ortamda çalıştırır.

        Args:
            komut (str): Çalıştırılacak komut.
            timeout (int, optional): Maksimum bekleme süresi (saniye).

        Returns:
            Any: Komut çıktısı. Türü backend'e göre değişir.

        Raises:
            NotImplementedError: Alt sınıf tarafından uygulanmalıdır.
        """
        raise NotImplementedError("execute() uygulanmamış")

    @abstractmethod
    def ping(self) -> bool:
        """Ortamın erişilebilir olup olmadığını kontrol eder.

        Returns:
            bool: Erişilebilir ise True, değilse False.
        """
        raise NotImplementedError("ping() uygulanmamış")

    @abstractmethod
    def bilgi(self) -> dict:
        """Ortam hakkında yapılandırılmış bilgi döndürür.

        Returns:
            dict: Ortam bilgilerini içeren sözlük.
        """
        raise NotImplementedError("bilgi() uygulanmamış")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
