# -*- coding: utf-8 -*-
"""gateway/platforms/__init__.py — Coklu Platform Kayit Defteri."""


__all__ = ['Callable', 'api_server', 'base', 'feishu_comment_rules', 'helpers', 'kaydet', 'mesaj_gonder', 'msgraph_webhook', 'platform_al', 'platform_baslat', 'platform_durdur', 'platform_listele', 'telegram', 'telegram_network', 'yuanbao_media']
from typing import Callable

from . import (
    telegram,
    telegram_network,
    base,
    helpers,
    feishu_comment_rules,
    msgraph_webhook,
    yuanbao_media,
    _http_client_limits,
    api_server,
)

_platformlar: dict[str, dict] = {}


def kaydet(ad: str, baslat: Callable, durdur: Callable, gonder: Callable):
    _platformlar[ad] = {
        "ad": ad,
        "baslat": baslat,
        "durdur": durdur,
        "gonder": gonder,
        "durum": "durdu",
    }


def platform_listele() -> list[str]:
    return list(_platformlar.keys())


def platform_al(ad: str) -> dict | None:
    return _platformlar.get(ad)


def platform_baslat(ad: str) -> bool:
    p = _platformlar.get(ad)
    if not p:
        return False
    try:
        p["baslat"]()
        p["durum"] = "calisiyor"
        return True
    except Exception:
        p["durum"] = "hata"
        return False


def platform_durdur(ad: str) -> bool:
    p = _platformlar.get(ad)
    if not p:
        return False
    try:
        p["durdur"]()
        p["durum"] = "durdu"
        return True
    except Exception:
        return False


def mesaj_gonder(ad: str, hedef: str, mesaj: str) -> str:
    p = _platformlar.get(ad)
    if not p:
        return f"[{ad}]: Platform tanimli degil."
    try:
        return p["gonder"](hedef, mesaj)
    except Exception as e:
        return f"[{ad}]: Hata: {e}"


# Tum platformlari otomatik kaydet
def _tumunu_kaydet():
    platform_mods = {
        "telegram": "gateway.platforms.telegram",
        "discord": "gateway.platforms.discord",
        "signal": "gateway.platforms.signal",
        "whatsapp": "gateway.platforms.whatsapp",
        "slack": "gateway.platforms.slack",
        "matrix": "gateway.platforms.matrix",
        "email": "gateway.platforms.email",
        "sms": "gateway.platforms.sms",
        "webhook": "gateway.platforms.webhook",
        "feishu": "gateway.platforms.feishu",
        "dingtalk": "gateway.platforms.dingtalk",
        "weixin": "gateway.platforms.weixin",
        "yuanbao": "gateway.platforms.yuanbao",
        "irc": "gateway.platforms.irc",
        "line": "gateway.platforms.line",
        "ntfy": "gateway.platforms.ntfy",
        "simplex": "gateway.platforms.simplex",
        "teams": "gateway.platforms.teams",
    }
    for ad, mod_path in platform_mods.items():
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            kaydet(
                ad,
                getattr(mod, "baslat", lambda: None),
                getattr(mod, "durdur", lambda: None),
                getattr(mod, "mesaj_gonder"),
            )
        except Exception:
            pass

_tumunu_kaydet()
