"""
tools.environments.ssh — SSH Uzak Ortamı

Paramiko ile SSH bağlantısı kurarak uzak sunucuda komut çalıştırır.
Paramiko opsiyoneldir; kurulu değilse uyarı verir.
Türkçe docstring ile belgelenmiştir.
"""

import logging
from typing import Any, Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)

try:
    import paramiko
    HAS_PARAMIKO = True
except (ImportError, NameError, AttributeError, Exception):
    HAS_PARAMIKO = False
    logger.warning("paramiko kurulu değil veya bu platformda desteklenmiyor. SSH ortamı kullanılamaz.")


class SSHEnvironment(BaseEnvironment):
    """SSH ile uzak sunucuda komut çalıştırır.

    Args:
        host (str): Uzak sunucu adresi.
        kullanici (str): Kullanıcı adı.
        sifre (str, optional): Parola.
        anahtar_yolu (str, optional): SSH anahtar dosya yolu.
    """

    def __init__(
        self,
        host: str = "localhost",
        kullanici: str = "root",
        sifre: Optional[str] = None,
        anahtar_yolu: Optional[str] = None,
    ):
        self.host = host
        self.kullanici = kullanici
        self.sifre = sifre
        self.anahtar_yolu = anahtar_yolu
        self._baglanti = None

    def _baglan(self):
        """SSH bağlantısını kurar (önbellekleme)."""
        if not HAS_PARAMIKO:
            raise RuntimeError("paramiko kurulu değil. pip install paramiko")
        if self._baglanti is not None:
            return self._baglanti
        self._baglanti = paramiko.SSHClient()
        self._baglanti.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        baglan_kw = {
            "hostname": self.host,
            "username": self.kullanici,
        }
        if self.sifre:
            baglan_kw["password"] = self.sifre
        if self.anahtar_yolu:
            baglan_kw["key_filename"] = self.anahtar_yolu
        try:
            self._baglanti.connect(**baglan_kw, timeout=10)
            logger.info(f"SSH bağlantısı kuruldu: {self.kullanici}@{self.host}")
        except Exception:
            self._baglanti = None
            raise
        return self._baglanti

    def execute(
        self,
        komut: str,
        host: Optional[str] = None,
        kullanici: Optional[str] = None,
        sifre: Optional[str] = None,
        anahtar_yolu: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> dict:
        """Uzak sunucuda komut çalıştırır.

        Args:
            komut (str): Çalıştırılacak komut.
            host (str, optional): Sunucu adresi (override).
            kullanici (str, optional): Kullanıcı adı (override).
            sifre (str, optional): Parola (override).
            anahtar_yolu (str, optional): SSH anahtar yolu (override).
            timeout (int, optional): Maksimum bekleme süresi.

        Returns:
            dict: {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "donus_kodu": int
            }
        """
        # Parametre override
        if host:
            self.host = host
        if kullanici:
            self.kullanici = kullanici
        if sifre:
            self.sifre = sifre
        if anahtar_yolu:
            self.anahtar_yolu = anahtar_yolu

        try:
            baglanti = self._baglan()
            stdin, stdout, stderr = baglanti.exec_command(komut, timeout=timeout)
            cikti = stdout.read().decode("utf-8", errors="replace")
            hata = stderr.read().decode("utf-8", errors="replace")
            donus_kodu = stdout.channel.recv_exit_status()
            return {
                "basarili": donus_kodu == 0,
                "cikti": cikti,
                "hata": hata,
                "donus_kodu": donus_kodu,
            }
        except Exception as e:
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "donus_kodu": -1,
            }

    def ping(self) -> bool:
        """SSH bağlantısını test eder.

        Returns:
            bool: Bağlantı başarılı ise True.
        """
        try:
            baglanti = self._baglan()
            transport = baglanti.get_transport()
            return transport is not None and transport.is_active()
        except Exception:
            return False

    def bilgi(self) -> dict:
        """SSH ortamı hakkında bilgi döndürür.

        Returns:
            dict: SSH bağlantı bilgileri.
        """
        return {
            "tur": "ssh",
            "host": self.host,
            "kullanici": self.kullanici,
            "paramiko_kurulu": HAS_PARAMIKO,
            "bagli": self._baglanti is not None,
            "aciklama": f"SSH uzak ortam ({self.kullanici}@{self.host})",
        }

    def __del__(self):
        if self._baglanti is not None:
            try:
                self._baglanti.close()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")


# Kolay kullanım için fonksiyonlar
def run(
    komut: str,
    host: str = "localhost",
    kullanici: str = "root",
    sifre: Optional[str] = None,
    anahtar_yolu: Optional[str] = None,
) -> dict:
    """Kısayol: SSHEnvironment().execute()"""
    return SSHEnvironment(
        host=host, kullanici=kullanici, sifre=sifre, anahtar_yolu=anahtar_yolu
    ).execute(komut)


def ping(host: str = "localhost", kullanici: str = "root") -> bool:
    """Kısayol: SSHEnvironment().ping()"""
    return SSHEnvironment(host=host, kullanici=kullanici).ping()
