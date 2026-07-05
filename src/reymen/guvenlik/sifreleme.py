# -*- coding: utf-8 -*-
"""
reymen/guvenlik/sifreleme.py â€” Fernet TabanlÄ± Konfigürasyon Åifreleme

encrypt_config() ve decrypt_config() fonksiyonlarÄ± ile
konfigürasyon verilerini (dict) simetrik olarak ÅŸifreler/çözer.

Anahtar .env'den (ENCRYPTION_KEY) okunur; yoksa otomatik oluÅŸturulup kaydedilir.
KullanÄ±m:
    from reymen.guvenlik.sifreleme import encrypt_config, decrypt_config

    sifreli = encrypt_config({"api_key": "gizli"})
    cozulmus = decrypt_config(sifreli)
"""

import json
import logging
import os
from pathlib import Path

from cryptography.fernet import Fernet

log = logging.getLogger(__name__)

# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# .env yolu (proje kökü)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/reymen/guvenlik â†’ proje kökü
_ENV_PATH = _PROJECT_ROOT / ".env"


def _load_or_create_key() -> bytes:
    """ENCRYPTION_KEY'i .env'den okur, yoksa oluÅŸturup .env'ye ekler."""
    env_path = _ENV_PATH
    key_var = "ENCRYPTION_KEY"

    # --- 1. Ã–nce os.environ / dotenv tarafÄ±ndan yüklenmiÅŸ olabilir ---
    raw = os.environ.get(key_var)
    if raw:
        return raw.encode("utf-8")

    # --- 2. .env dosyasÄ±nÄ± manuel satÄ±r satÄ±r oku ---
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{key_var}="):
                raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                return raw.encode("utf-8")

    # --- 3. Hiçbiri yoksa yeni anahtar oluÅŸtur ---
    log.info("ENCRYPTION_KEY bulunamadÄ±, yeni Fernet anahtarÄ± oluÅŸturuluyor...")
    new_key = Fernet.generate_key()  # bytes (URL-safe base64, 44 karakter)
    key_line = f"{key_var}={new_key.decode('utf-8')}"

    # .env sonuna ekle (dosya yoksa oluÅŸtur)
    if env_path.exists():
        existing = env_path.read_text("utf-8").rstrip("\n")
        # BoÅŸlukla ayÄ±r
        if existing and not existing.endswith("\n"):
            existing += "\n"
        env_path.write_text(f"{existing}\n{key_line}\n", "utf-8")
    else:
        env_path.write_text(f"# ReYMeN â€” Environment Variables\n{key_line}\n", "utf-8")

    log.info("Yeni ENCRYPTION_KEY %s dosyasÄ±na kaydedildi.", env_path)
    return new_key


def encrypt_config(data: dict) -> str:
    """
    Verilen sözlüÄŸü Fernet simetrik anahtarÄ± ile ÅŸifreler.

    Args:
        data: Åifrelenecek konfigürasyon sözlüÄŸü (JSON-serializable olmalÄ±).

    Returns:
        ÅifrelenmiÅŸ token (str).
    """
    key = _load_or_create_key()
    cipher = Fernet(key)
    payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    token = cipher.encrypt(payload)
    return token.decode("utf-8")


def decrypt_config(token: str) -> dict:
    """
    Fernet ile ÅŸifrelenmiÅŸ token'Ä± çözer.

    Args:
        token: encrypt_config() tarafÄ±ndan üretilmiÅŸ ÅŸifreli string.

    Returns:
        Orijinal konfigürasyon sözlüÄŸü.
    """
    key = _load_or_create_key()
    cipher = Fernet(key)
    payload = cipher.decrypt(token.encode("utf-8"))
    return json.loads(payload.decode("utf-8"))
