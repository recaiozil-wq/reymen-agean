# -*- coding: utf-8 -*-
"""
telegram_bot/ai_bot.py — ReYMeN AI Agent Botu (Redirect).

Bu dosya yalnizca yonlendirme icindir.
Tum ozellikler: reymen/ag/telegram_bot
"""

from reymen.ag.telegram_bot import (
    BotProcess,
    UnifiedBot,
    CronManager,
    _cron_manager,
    _api,
    gonder,
    gonder_requests,
    BEYIN_CLS,
    ONCE_HAFIZA_ARA,
    ONCE_HAFIZA_KAYDET,
    CONVERSATION_LOOP_CLS,
    TOKEN,
    CHAT_ID,
    API_BASE,
    GATEWAY_MOD,
    _PROJE_KOK,
)


def main():
    """BotProcess AI modu baslat."""
    if not TOKEN or TOKEN.startswith("***"):
        import sys
        print("[ai_bot] TELEGRAM_BOT_TOKEN ayarli degil!")
        sys.exit(1)
    bot = BotProcess(TOKEN)
    bot.poll()

if __name__ == "__main__":
    main()
