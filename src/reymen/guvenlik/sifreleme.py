# -*- coding: utf-8 -*-
"""
reymen/guvenlik/sifreleme.py — Fernet Tabanlı Konfigürasyon Şifreleme

encrypt_config() ve decrypt_config() fonksiyonları ile
konfigürasyon verilerini (dict) simetrik olarak şifreler/çözer.

Anahtar .env'den (ENCRYPTION_KEY) okunur; yoksa otomatik oluşturulup kaydedilir.
Kullanım:
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

# ──────────────────────────────────────────────
# .env yolu (proje kökü)
# ──────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # src/reymen/guvenlik → proje kökü
_ENV_PATH = _PROJECT_ROOT / ".env"


def _load_or_create_key() -> bytes:
    """ENCRYPTION_KEY'i .env'den okur, yoksa oluşturup .env'ye ekler."""
    env_path = _ENV_PATH
    key_var = "ENCRYPTION_KEY"

    # --- 1. Önce os.environ / dotenv tarafından yüklenmiş olabilir ---
    raw = os.environ.get(key_var)
    if raw:
        return raw.encode("utf-8")

    # --- 2. .env dosyasını manuel satır satır oku ---
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            line = line.strip()
            if line.startswith(f"{key_var}="):
                raw = line.split("=", 1)[1].strip().strip('"').strip("'")
                return raw.encode("utf-8")

    # --- 3. Hiçbiri yoksa yeni anahtar oluştur ---
    log.info("ENCRYPTION_KEY bulunamadı, yeni Fernet anahtarı oluşturuluyor...")
    new_key = Fernet.generate_key()  # bytes (URL-safe base64, 44 karakter)
    key_line = f"{key_var}={new_key.decode('utf-8')}"

    # .env sonuna ekle (dosya yoksa oluştur)
    if env_path.exists():
        existing = env_path.read_text("utf-8").rstrip("\n")
        # Boşlukla ayır
        if existing and not existing.endswith("\n"):
            existing += "\n"
        env_path.write_text(f"{existing}\n{key_line}\n", "utf-8")
    else:
        env_path.write_text(f"# ReYMeN — Environment Variables\n{key_line}\n", "utf-8")

    log.info("Yeni ENCRYPTION_KEY %s dosyasına kaydedildi.", env_path)
    return new_key


def encrypt_config(data: dict) -> str:
    """
    Verilen sözlüğü Fernet simetrik anahtarı ile şifreler.

    Args:
        data: Şifrelenecek konfigürasyon sözlüğü (JSON-serializable olmalı).

    Returns:
        Şifrelenmiş token (str).
    """
    key = _load_or_create_key()
    cipher = Fernet(key)
    payload = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
    token = cipher.encrypt(payload)
    return token.decode("utf-8")


def decrypt_config(token: str) -> dict:
    """
    Fernet ile şifrelenmiş token'ı çözer.

    Args:
        token: encrypt_config() tarafından üretilmiş şifreli string.

    Returns:
        Orijinal konfigürasyon sözlüğü.
    """
    key = _load_or_create_key()
    cipher = Fernet(key)
    payload = cipher.decrypt(token.encode("utf-8"))
    return json.loads(payload.decode("utf-8"))
