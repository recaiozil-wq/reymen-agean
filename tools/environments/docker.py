"""
tools.environments.docker — Docker Konteyner Ortamı

Docker CLI veya SDK ile konteyner yönetimi sağlar.
docker SDK'sı opsiyoneldir; yoksa subprocess ile docker CLI kullanılır.
Türkçe docstring ile belgelenmiştir.
"""

import logging
import subprocess
from typing import Any, Optional

from tools.environments.base import BaseEnvironment

logger = logging.getLogger(__name__)

try:
    import docker  # noqa: F401
    HAS_DOCKER_SDK = True
except ImportError:
    HAS_DOCKER_SDK = False
    logger.debug("docker SDK kurulu değil. CLI modu kullanılacak.")


class DockerEnvironment(BaseEnvironment):
    """Docker konteyner ortamı.

    Komutları bir Docker imajı içinde çalıştırır.
    docker SDK'sı varsa onu, yoksa docker CLI'ı kullanır.

    Args:
        imaj (str): Docker imaj adı.
        tag (str): İmaj etiketi (varsayılan: "latest").
    """

    def __init__(self, imaj: str = "python:3.11-slim", tag: str = "latest"):
        self.imaj = imaj
        self.tag = tag
        self._imaj_etiket = f"{imaj}:{tag}"

    def execute(
        self,
        komut: str,
        imaj: Optional[str] = None,
        tag: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> dict:
        """Docker konteyner içinde komut çalıştırır.

        Args:
            komut (str): Çalıştırılacak komut.
            imaj (str, optional): İmaj adı (override).
            tag (str, optional): İmaj etiketi (override).
            timeout (int, optional): Maksimum bekleme süresi.

        Returns:
            dict: {
                "basarili": bool,
                "cikti": str,
                "hata": str,
                "donus_kodu": int
            }
        """
        if imaj:
            self.imaj = imaj
        if tag:
            self.tag = tag
        self._imaj_etiket = f"{self.imaj}:{self.tag}"

        if HAS_DOCKER_SDK:
            return self._sdk_execute(komut, timeout)
        else:
            return self._cli_execute(komut, timeout)

    def _cli_execute(self, komut: str, timeout: Optional[int] = None) -> dict:
        """docker CLI ile komut çalıştırır."""
        try:
            docker_komut = [
                "docker", "run", "--rm",
                self._imaj_etiket,
                "sh", "-c", komut,
            ]
            sonuc = subprocess.run(
                docker_komut,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return {
                "basarili": sonuc.returncode == 0,
                "cikti": sonuc.stdout,
                "hata": sonuc.stderr,
                "donus_kodu": sonuc.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "basarili": False,
                "cikti": "",
                "hata": f"Zaman aşımı ({timeout}s)",
                "donus_kodu": -1,
            }
        except FileNotFoundError:
            return {
                "basarili": False,
                "cikti": "",
                "hata": "docker bulunamadı. Docker kurulu olduğundan emin olun.",
                "donus_kodu": -1,
            }
        except Exception as e:
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "donus_kodu": -1,
            }

    def _sdk_execute(self, komut: str, timeout: Optional[int] = None) -> dict:
        """docker Python SDK ile komut çalıştırır."""
        try:
            import docker
            client = docker.from_env()
            container = client.containers.run(
                self._imaj_etiket,
                command=["sh", "-c", komut],
                detach=False,
                remove=True,
            )
            # SDK üzerinden çıktı al
            cikti = container.decode("utf-8", errors="replace") if isinstance(container, bytes) else str(container)
            return {
                "basarili": True,
                "cikti": cikti,
                "hata": "",
                "donus_kodu": 0,
            }
        except Exception as e:
            return {
                "basarili": False,
                "cikti": "",
                "hata": str(e),
                "donus_kodu": -1,
            }

    def ping(self) -> bool:
        """Docker'ın kullanılabilir olup olmadığını kontrol eder.

        Returns:
            bool: Docker erişilebilir ise True.
        """
        try:
            if HAS_DOCKER_SDK:
                import docker
                client = docker.from_env()
                client.ping()
                return True
            else:
                sonuc = subprocess.run(
                    ["docker", "info"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                return sonuc.returncode == 0
        except Exception:
            return False

    def bilgi(self) -> dict:
        """Docker ortamı hakkında bilgi döndürür.

        Returns:
            dict: Docker yapılandırma bilgileri.
        """
        return {
            "tur": "docker",
            "imaj": self.imaj,
            "tag": self.tag,
            "imaj_etiket": self._imaj_etiket,
            "sdk_kurulu": HAS_DOCKER_SDK,
            "aciklama": f"Docker konteyner ortamı ({self._imaj_etiket})",
        }


# Kolay kullanım için fonksiyonlar
def run(komut: str, imaj: str = "python:3.11-slim", tag: str = "latest") -> dict:
    """Kısayol: DockerEnvironment().execute()"""
    return DockerEnvironment(imaj=imaj, tag=tag).execute(komut)


def ping() -> bool:
    """Kısayol: DockerEnvironment().ping()"""
    return DockerEnvironment().ping()
