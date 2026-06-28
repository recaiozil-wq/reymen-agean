# -*- coding: utf-8 -*-
"""plugins/platforms/__init__.py — Platform Plugin Kayit Defteri.

Tum platform pluginlerini import eder ve motor_kaydet() uzerinden kaydeder.
Platformlar: Discord, Mattermost, IRC, ntfy
"""


__all__ = ['motor_kaydet']
import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "platforms"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Platform pluginlerini yoneten kayit defteri"

_platforms = []

try:
    from plugins.platforms import discord as _discord
    _platforms.append(_discord)
except ImportError:
    logger.debug("discord platformu yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.platforms import mattermost as _mattermost
    _platforms.append(_mattermost)
except ImportError:
    logger.debug("mattermost platformu yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.platforms import irc as _irc
    _platforms.append(_irc)
except ImportError:
    logger.debug("irc platformu yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.platforms import ntfy as _ntfy
    _platforms.append(_ntfy)
except ImportError:
    logger.debug("ntfy platformu yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")


def motor_kaydet(motor):
    """Tum platform pluginlerini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    kayit_sayisi = 0
    for platform in _platforms:
        try:
            if hasattr(platform, "motor_kaydet"):
                platform.motor_kaydet(motor)
                kayit_sayisi += 1
        except Exception as e:
            logger.warning("Platform kayit hatasi: %s", e)
    logger.info("[Plugin:platforms] %d platform kayit edildi.", kayit_sayisi)
