"""
tools.environments.file_sync — Dosya Senkronizasyon

Local ile Remote arasında dosya kopyalama işlemleri.
Türkçe docstring ile belgelenmiştir.
"""

import logging
import os
import shutil
from typing import Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


class FileSyncEnvironment(BaseEnvironment):
    """Local↔Remote dosya senkronizasyon ortamı.

    Kaynak ve hedef arasında dosya kopyalama işlemleri yapar.
    Yerel yerel, yerel uzak ve uzak yerel kopyalama desteklenir.
    """

    def sync(
        self,
        kaynak: str,
        hedef: str,
        yon: str = "lokal->remote",
        host: Optional[str] = None,
        kullanici: Optional[str] = None,
        sifre: Optional[str] = None,
        anahtar_yolu: Optional[str] = None,
    ) -> dict:
        """Dosyaları kaynaktan hedefe senkronize eder.

        Args:
            kaynak (str): Kaynak dosya/dizin yolu.
            hedef (str): Hedef dosya/dizin yolu.
            yon (str): Senkronizasyon yönü:
                "lokal->remote" (yerelden uzaga),
                "remote->lokal" (uzaktan yerele),
                "lokal->lokal" (yerel kopyalama).
            host (str, optional): Uzak sunucu adresi.
            kullanici (str, optional): SSH kullanıcı adı.
            sifre (str, optional): SSH parolası.
            anahtar_yolu (str, optional): SSH anahtar yolu.

        Returns:
            dict: {
                "basarili": bool,
                "mesaj": str,
                "kaynak": str,
                "hedef": str,
                "yon": str
            }
        """
        try:
            if yon == "lokal->lokal":
                return self._yerel_kopyala(kaynak, hedef)
            elif yon in ("lokal->remote", "remote->lokal"):
                return self._uzak_kopyala(kaynak, hedef, yon, host, kullanici, sifre, anahtar_yolu)
            else:
                return {
                    "basarili": False,
                    "mesaj": f"Geçersiz yön: '{yon}'. Şunlardan biri olmalı: lokal->lokal, lokal->remote, remote->lokal",
                    "kaynak": kaynak,
                    "hedef": hedef,
                    "yon": yon,
                }
        except Exception as e:
            return {
                "basarili": False,
                "mesaj": str(e),
                "kaynak": kaynak,
                "hedef": hedef,
                "yon": yon,
            }

    def _yerel_kopyala(self, kaynak: str, hedef: str) -> dict:
        """Yerel dosya/dizin kopyalama."""
        if os.path.isdir(kaynak):
            shutil.copytree(kaynak, hedef, dirs_exist_ok=True)
        else:
            os.makedirs(os.path.dirname(hedef), exist_ok=True)
            shutil.copy2(kaynak, hedef)
        return {
            "basarili": True,
            "mesaj": f"Kopyalandı: {kaynak} -> {hedef}",
            "kaynak": kaynak,
            "hedef": hedef,
            "yon": "lokal->lokal",
        }

    def _uzak_kopyala(
        self,
        kaynak: str,
        hedef: str,
        yon: str,
        host: Optional[str],
        kullanici: Optional[str],
        sifre: Optional[str],
        anahtar_yolu: Optional[str],
    ) -> dict:
        """SSH üzerinden dosya kopyalama (SFTP)."""
        if not HAS_PARAMIKO:
            return {
                "basarili": False,
                "mesaj": "paramiko kurulu değil. pip install paramiko",
                "kaynak": kaynak,
                "hedef": hedef,
                "yon": yon,
            }
        if not host or not kullanici:
            return {
                "basarili": False,
                "mesaj": "Uzak kopyalama için host ve kullanici gerekli",
                "kaynak": kaynak,
                "hedef": hedef,
                "yon": yon,
            }

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        baglan_kw = {"hostname": host, "username": kullanici}
        if sifre:
            baglan_kw["password"] = sifre
        if anahtar_yolu:
            baglan_kw["key_filename"] = anahtar_yolu
        ssh.connect(**baglan_kw, timeout=10)

        sftp = ssh.open_sftp()
        try:
            if yon == "lokal->remote":
                sftp.put(kaynak, hedef)
                mesaj = f"Yüklendi: {kaynak} -> {hedef} (uzak)"
            else:
                sftp.get(kaynak, hedef)
                mesaj = f"İndirildi: {kaynak} (uzak) -> {hedef}"
            return {
                "basarili": True,
                "mesaj": mesaj,
                "kaynak": kaynak,
                "hedef": hedef,
                "yon": yon,
            }
        finally:
            sftp.close()
            ssh.close()

    def execute(self, komut: str, timeout: Optional[int] = None) -> dict:
        """FileSync için execute, sync işlemine yönlendirir.

        Args:
            komut (str): "kaynak->hedef" formatında sync talimatı.
            timeout (int, optional): Kullanılmaz.

        Returns:
            dict: sync() çıktısı.
        """
        # Basit ayrıştırma: "kaynak->hedef"
        if "->" in komut:
            parts = komut.split("->", 1)
            return self.sync(kaynak=parts[0].strip(), hedef=parts[1].strip())
        return {
            "basarili": False,
            "mesaj": "Geçersiz format. 'kaynak->hedef' kullanın",
            "cikti": "",
            "hata": "",
            "donus_kodu": -1,
        }

    def ping(self) -> bool:
        """Dosya senkronizasyonunun kullanılabilir olduğunu kontrol eder.

        Returns:
            bool: Her zaman True (yerel dosya sistemi mevcut).
        """
        return True

    def bilgi(self) -> dict:
        """FileSync ortamı hakkında bilgi döndürür.

        Returns:
            dict: Yapılandırma bilgileri.
        """
        return {
            "tur": "file_sync",
            "paramiko_kurulu": HAS_PARAMIKO,
            "desteklenen_yonler": ["lokal->lokal", "lokal->remote", "remote->lokal"],
            "aciklama": "Yerel ve uzak dosya senkronizasyon ortamı",
        }


# Kolay kullanım için fonksiyonlar
def sync(kaynak: str, hedef: str, yon: str = "lokal->lokal") -> dict:
    """Kısayol: FileSyncEnvironment().sync()"""
    return FileSyncEnvironment().sync(kaynak=kaynak, hedef=hedef, yon=yon)


def ping() -> bool:
    """Kısayol: FileSyncEnvironment().ping()"""
    return FileSyncEnvironment().ping()
