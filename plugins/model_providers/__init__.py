# -*- coding: utf-8 -*-
"""plugins/model_providers/__init__.py — Model Saglayici Kayit Defteri.

Tum model saglayici pluginlerini import eder ve motor_kaydet() uzerinden kaydeder.
"""


__all__ = ['motor_kaydet']
import logging

logger = logging.getLogger(__name__)

PLUGIN_ADI = "model_providers"
PLUGIN_VERSIYON = "1.0.0"
PLUGIN_ACIKLAMA = "Model saglayici pluginlerini yoneten kayit defteri"

# Tum saglayicilari import et
_providers = []

try:
    from plugins.model_providers import openai as _openai_provider
    _providers.append(_openai_provider)
except ImportError:
    logger.debug("openai provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import anthropic as _anthropic_provider
    _providers.append(_anthropic_provider)
except ImportError:
    logger.debug("anthropic provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import deepseek as _deepseek_provider
    _providers.append(_deepseek_provider)
except ImportError:
    logger.debug("deepseek provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import gemini as _gemini_provider
    _providers.append(_gemini_provider)
except ImportError:
    logger.debug("gemini provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import openrouter as _openrouter_provider
    _providers.append(_openrouter_provider)
except ImportError:
    logger.debug("openrouter provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import groq as _groq_provider
    _providers.append(_groq_provider)
except ImportError:
    logger.debug("groq provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import xai as _xai_provider
    _providers.append(_xai_provider)
except ImportError:
    logger.debug("xai provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import mistral as _mistral_provider
    _providers.append(_mistral_provider)
except ImportError:
    logger.debug("mistral provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")

try:
    from plugins.model_providers import together as _together_provider
    _providers.append(_together_provider)
except ImportError:
    logger.debug("together provider yuklenemedi")
except Exception:
    logger.warning("[fix_01_sessiz_except] Exception")


def motor_kaydet(motor):
    """Tum model saglayici pluginlerini motor'a kaydeder.

    Args:
        motor: Motor ornegi
    """
    kayit_sayisi = 0
    for provider in _providers:
        try:
            if hasattr(provider, "motor_kaydet"):
                provider.motor_kaydet(motor)
                kayit_sayisi += 1
        except Exception as e:
            logger.warning("Provider kayit hatasi: %s", e)
    logger.info("[Plugin:model_providers] %d provider kayit edildi.", kayit_sayisi)
