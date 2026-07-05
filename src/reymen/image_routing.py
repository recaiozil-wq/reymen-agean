# -*- coding: utf-8 -*-
"""Gorsel uretim routing — prompt'a gore en uygun provider'i sec.

Hermes agent/image_routing.py'den adapte edilmistir.
"""
from __future__ import annotations
import logging
from typing import Optional
from reymen.image_gen_registry import list_providers, get_provider

logger = logging.getLogger(__name__)

def route(prompt: str, preferred: Optional[str] = None) -> Optional[str]:
    """Prompt'a gore en uygun gorsel uretim provider'ini sec.

    Args:
        prompt: Gorsel prompt
        preferred: Tercih edilen provider (varsa)

    Returns:
        Provider adi veya None
    """
    providers = list_providers()
    if not providers:
        return None
    if preferred and preferred in providers:
        return preferred
    return providers[0]

def generate(prompt: str, provider: Optional[str] = None, **kwargs) -> Optional[str]:
    """Gorsel olustur.

    Args:
        prompt: Gorsel prompt
        provider: Provider adi (None=auto)

    Returns:
        Gorsel URL veya None
    """
    provider_name = route(prompt, preferred=provider)
    if not provider_name:
        return None
    fn = get_provider(provider_name)
    if not fn:
        return None
    try:
        return fn(prompt, **kwargs)
    except Exception as e:
        logger.warning("Image gen hatasi (%s): %s", provider_name, e)
        return None
