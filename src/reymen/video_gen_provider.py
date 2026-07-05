# -*- coding: utf-8 -*-
"""Video uretim Provider ABC.

Hermes agent/video_gen_provider.py'den adapte edilmistir.
"""
from __future__ import annotations
import abc
from typing import Any, Dict, Optional

class VideoGenProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str: ...

    @abc.abstractmethod
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """Video olustur. URL dondur."""
