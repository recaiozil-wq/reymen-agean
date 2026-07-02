#!/usr/bin/env python3
"""Ornek 1: Plugin sistemi kullanimi — ozel bir plugin yaz ve yukle."""
from src.reymen.plugin import PluginBase
from src.reymen.plugin.manager import PluginManager

class SifreliPlugin(PluginBase):
    name = "sifreli"
    version = "1.0"
    def on_message(self, message: str, context: dict) -> str:
        return message.replace("sifre", "****")

pm = PluginManager()
pm.kaydet(SifreliPlugin())
print("Plugin yuklendi. /sifre komutu aktif.")
