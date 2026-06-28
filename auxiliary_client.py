# -*- coding: utf-8 -*-
"""SHIM — agent/auxiliary_client.py yönlendirir"""
from agent.auxiliary_client import *  # noqa: F401, F403


class AuxiliaryClient:
    """Yardımcı HTTP istemcisi stub."""

    def get(self, url: str, **kwargs):
        return None

    def post(self, url: str, **kwargs):
        return None
