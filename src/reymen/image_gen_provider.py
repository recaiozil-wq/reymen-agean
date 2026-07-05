# -*- coding: utf-8 -*-
"""Gorsel uretim provider ABC + FAL provider.

Hermes agent/image_gen_provider.py'den adapte.
"""
from __future__ import annotations
import abc
from typing import Optional

class ImageGenProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...
    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]: ...

class FALProvider(ImageGenProvider):
    @property
    def name(self): return "fal"
    def generate(self, prompt, **kwargs):
        try:
            import fal_client
            return fal_client.run("fal-ai/flux", arguments={"prompt": prompt})
        except Exception:
            return None
