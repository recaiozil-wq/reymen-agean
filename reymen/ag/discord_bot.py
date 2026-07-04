# -*- coding: utf-8 -*-
"""
reymen/ag/discord_bot.py — Discord Bot Gateway Wrapper (DiscordAdapter yolu).

Bu dosya, src/reymen/ag/discord_bot.py'ye yonlendirme amaciyla
DiscordAdapter (src/core/gateway_manager.py) tarafindan kullanilir.
"""
import sys
import os

# Ust dizine ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from reymen.ag.discord_bot import *  # noqa: F401, F403
from reymen.ag.discord_bot import motor_kaydet as _mk  # noqa: F401

if __name__ == "__main__":
    from reymen.ag.discord_bot import main
    main()
