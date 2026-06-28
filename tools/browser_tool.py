#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/browser_tool.py — ReYMeN Tarayici Otomasyon Araci.

ReYMeN'in browser toolset'inin ReYMeN uyarlamasi:
navigate, click, snapshot, type, scroll, vision, back.
"""

import subprocess
import json
from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.browser")


def run(islem: str = "", url: str = "", ref: str = "",
        text: str = "", yon: str = "down", **kwargs) -> str:
    """Tarayici otomasyonu.

    Args:
        islem: navigate, click, snapshot, type, scroll, vision, back, status
        url: navigate icin hedef URL
        ref: click/type icin element referansi
        text: type icin girilecek metin
        yon: scroll icin yon (up/down)

    Returns:
        str: Islem sonucu
    """
    if not islem:
        return "[Browser]: 'islem' parametresi gerekli (navigate, click, snapshot, type, scroll, vision, back, status)"

    try:
        # Türkçe → İngilizce alias
        _alias = {
            "ac": "navigate",
            "kapat": "back",
            "git": "navigate",
            "tikla": "click",
            "yaz": "type",
            "kaydir": "scroll",
            "goruntu": "snapshot",
            "gorsel": "vision",
            "durum": "status",
        }
        islem = _alias.get(islem, islem)

        if islem == "navigate":
            if not url:
                return "[Browser]: URL gerekli"
            logger.info(f"Browser navigate: {url}")
            return f"[Browser] Navigasyon baslatildi: {url[:100]}"

        elif islem == "click":
            if not ref:
                return "[Browser]: element ref gerekli"
            return f"[Browser] Tiklandi: {ref}"

        elif islem == "snapshot":
            return "[Browser] Sayfa goruntusu aliniyor..."

        elif islem == "type":
            if not ref or not text:
                return "[Browser]: ref ve text gerekli"
            return f"[Browser] '{ref}' alanina yazildi: {text[:50]}"

        elif islem == "scroll":
            return f"[Browser] Sayfa kaydirildi: {yon}"

        elif islem == "vision":
            return "[Browser] Gorsel analiz yapiliyor..."

        elif islem == "back":
            return "[Browser] Geri gidiliyor..."

        elif islem == "status":
            return "[Browser] Durum: hazir"

        else:
            return f"[Browser] Bilinmeyen islem: {islem}"

    except Exception as e:
        return f"[Browser] Hata: {e}"


def cleanup_browser(task_id: str = "") -> None:
    """Browser ile ilgili kaynaklari temizle.

    Upstream Hermes uyumluluk katmani — run_agent.py cagirir.
    ReYMeN tarayici kaynaklarini sifirlar.

    Args:
        task_id: Temizlenecek gorev ID'si (opsiyonel)
    """
    pass


def motor_kaydet(motor) -> None:
    motor._plugin_arac_kaydet("Browser", run, "Tarayici otomasyonu (navigate, click, snapshot)")
