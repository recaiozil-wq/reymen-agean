"""Guvenlik katmani - approvals, izinler."""

import os, json
from pathlib import Path

CONFIG_DIR = Path.home() / ".deepseek_ajan"
CONFIG_FILE = CONFIG_DIR / "guvenlik.json"

_DEFAULT_CONFIG = {
    "allow_all_users": False,
    "allowed_users": [],
    "approvals_mode": "strict",
    "auto_approve_commands": [],
    "max_py_execution_time": 30,
    "max_sys_execution_time": 30,
    "log_all_commands": True,
}


def _load():
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            return {**_DEFAULT_CONFIG, **data}
        except Exception:
            pass
    return dict(_DEFAULT_CONFIG)


def _save(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False))


def get(key):
    return _load().get(key, _DEFAULT_CONFIG.get(key))


def set_key(key, value):
    cfg = _load()
    cfg[key] = value
    _save(cfg)
    return True


def yetki_kontrol(user_id=None):
    """Kullanim izni kontrolu. user_id=None = yerel kullanici."""
    cfg = _load()
    if cfg["allow_all_users"]:
        return True
    if user_id is None:
        return True
    if user_id in cfg["allowed_users"]:
        return True
    return False


def onay_gerekli(komut_tipi):
    """Bu komut tipi icin onay gerekli mi?"""
    cfg = _load()
    if cfg["approvals_mode"] == "off":
        return False
    if cfg["approvals_mode"] == "strict":
        return True
    if komut_tipi in cfg.get("auto_approve_commands", []):
        return False
    return True


def durum():
    cfg = _load()
    mode = cfg["approvals_mode"]
    users = "herkes" if cfg["allow_all_users"] else "sadece yerel"
    return f"approvals={mode}, erisim={users}"


def reset():
    _save(dict(_DEFAULT_CONFIG))
    return True
