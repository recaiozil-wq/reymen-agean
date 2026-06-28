# -*- coding: utf-8 -*-
"""ornek_tool.py — Ornek plugin.

PluginManager ile yuklenebilir. run() fonksiyonu zorunludur.
"""


def run(target: str = "world") -> str:
    return f"Hello, {target}!"
