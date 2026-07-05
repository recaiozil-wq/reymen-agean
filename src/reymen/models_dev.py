# -*- coding: utf-8 -*-
"""Gelistirici model listesi.

Hermes agent/models_dev.py'den adapte edilmistir.
"""
from __future__ import annotations

DEV_MODELS = ["deepseek-v4-flash", "mimo-v2.5-pro", "lmstudio"]

def dev_model_mi(model: str) -> bool:
    return model in DEV_MODELS
