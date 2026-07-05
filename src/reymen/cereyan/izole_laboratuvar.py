# -*- coding: utf-8 -*-
"""
izole_laboratuvar.py â€” Docker Python sandbox.
DÃœZELTME (HATA 2 / KRÄ°TÄ°K): Kök dizine (/) mount KALDIRILDI.
ArtÄ±k /workspace altÄ±na bind ediliyor; container host kök dosyalarÄ±na yazamaz.
Docker yoksa import hata vermez (DOCKER_AVAILABLE=False), local'e düÅŸülür.
"""

import os
import uuid
import subprocess

try:
    import docker

    DOCKER_AVAILABLE = True
    # Daemon gerçekten çalÄ±ÅŸÄ±yor mu kontrol et
    try:
        docker.from_env().ping()
    except Exception:
        DOCKER_AVAILABLE = False
except ImportError:
    DOCKER_AVAILABLE = False


def izole_python_calistir(kod, image="python:3.10-slim", timeout=60):
    """Python kodunu izole çalÄ±ÅŸtÄ±rÄ±r. Docker varsa container'da, yoksa local subprocess."""
    dosya_adi = f"_ReYMeN_{uuid.uuid4().hex[:8]}.py"
    current_dir = os.getcwd()
    tam_yol = os.path.join(current_dir, dosya_adi)
    with open(tam_yol, "w", encoding="utf-8") as f:
        f.write(kod)
    try:
        if DOCKER_AVAILABLE:
            return _docker_run(dosya_adi, current_dir, image, timeout)
        return _local_run(tam_yol, timeout)
    finally:
        if os.path.exists(tam_yol):
            os.remove(tam_yol)


def _docker_run(dosya_adi, current_dir, image, timeout):
    client = docker.from_env()
    try:
        cikti = client.containers.run(
            image,
            command=f"python /workspace/{dosya_adi}",
            volumes={current_dir: {"bind": "/workspace", "mode": "rw"}},  # KÃ–K DEÄÄ°L
            working_dir="/workspace",
            remove=True,
            stdout=True,
            stderr=True,
        )
        return cikti.decode("utf-8", errors="replace")
    except Exception as e:
        return f"[Sandbox Hata]: {e}"


def _local_run(tam_yol, timeout):
    try:
        sonuc = subprocess.run(
            ["python", tam_yol],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding="utf-8",
            errors="replace",
        )
        return f"[Ã‡IKTI]\n{sonuc.stdout}\n[HATA]\n{sonuc.stderr}".strip()
    except subprocess.TimeoutExpired:
        return "[Hata]: Sandbox zaman aÅŸÄ±mÄ±."


if __name__ == "__main__":
    print(izole_python_calistir("print('ReYMeN sandbox çalÄ±ÅŸÄ±yor')"))
