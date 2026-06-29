# -*- coding: utf-8 -*-
"""🤖 ReYMeN Telegram Bot — AIAgentOrchestrator ile çalışan bot.

Kullanim:
    BOT_TOKEN=*** BOT_AD="@Pasa_38_bot" python -m reymen.telegram_bot

Ortam degiskenleri:
    BOT_TOKEN  — Telegram bot token
    BOT_AD     — Bot adi (opsiyonel, debug icin)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

_PROJE_KOK = Path(__file__).resolve().parent.parent.parent
if str(_PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(_PROJE_KOK))

from dotenv import load_dotenv

_env_dosyasi = _PROJE_KOK / ".env"
if _env_dosyasi.exists():
    load_dotenv(_env_dosyasi, override=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
)
log = logging.getLogger("reymen_bot")


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------
class ReYMeNTelegramBot:
    """Tek Telegram botu — AIAgentOrchestrator ile."""

    def __init__(self, token: str, bot_ad: str = ""):
        self.token = token
        self.bot_ad = bot_ad or token[:10]
        self._agent = None
        self._app = None
        log.info("[%s] Baslatiliyor...", self.bot_ad)

    def _agent_al(self):
        if self._agent is None:
            from reymen.sistem.main import AIAgentOrchestrator
            self._agent = AIAgentOrchestrator(
                config=None, backend_mode="local", max_tur=15, onay_iste=False,
            )
            log.info("[%s] AIAgentOrchestrator hazir", self.bot_ad)
        return self._agent

    def baslat(self):
        from telegram import Update
        from telegram.ext import Application, CommandHandler, MessageHandler, filters

        self._app = Application.builder().token(self.token).build()
        self._app.add_handler(CommandHandler("start", self._cmd_start))
        self._app.add_handler(CommandHandler("yardim", self._cmd_yardim))
        self._app.add_handler(CommandHandler("temizle", self._cmd_temizle))
        self._app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._mesaj_al))
        log.info("[%s] Polling...", self.bot_ad)
        self._app.run_polling(drop_pending_updates=True)

    async def _cmd_start(self, update, context):
        await update.message.reply_text(
            "🤖 *ReYMeN Bot*\n\nReYMeN AI asistanina hos geldin.\n"
            "`/yardim` — Yardim\n`/temizle` — Konusma gecmisini sifirla",
            parse_mode="Markdown",
        )

    async def _cmd_yardim(self, update, context):
        await update.message.reply_text(
            "🤖 *ReYMeN Bot*\n\nMesaj yaz → sohbet et, soru sor.\n"
            "`/temizle` — Gecmisi sifirla",
            parse_mode="Markdown",
        )

    async def _cmd_temizle(self, update, context):
        agent = self._agent_al()
        agent.session_temizle()
        await update.message.reply_text("✅ Konusma gecmisi temizlendi.")

    async def _mesaj_al(self, update, context):
        hedef = update.message.text.strip()
        if not hedef:
            return
        try:
            # ConversationLoop ile ensemble akisi (DeepSeek + OnceHafiza + Web + Cache karsilastirmali)
            from reymen.cereyan.conversation_loop import ConversationLoop
            loop = ConversationLoop()
            sonuc = loop.run_conversation(hedef)
            yanit = sonuc.get("yanit", "") or sonuc.get("output", "") or "Yanit alinamadi."
            await update.message.reply_text(str(yanit)[:4000])
        except Exception as e:
            log.error("[%s] Hata: %s", self.bot_ad, e)
            await update.message.reply_text(f"❌ Hata: {e}")


# ---------------------------------------------------------------------------
# Ana
# ---------------------------------------------------------------------------
def main():
    token = os.environ.get("BOT_TOKEN", "").strip()
    if not token:
        log.error("❌ BOT_TOKEN ortam degiskeni gerekli")
        sys.exit(1)
    bot_ad = os.environ.get("BOT_AD", "Bot")
    bot = ReYMeNTelegramBot(token=token, bot_ad=bot_ad)
    bot.baslat()


if __name__ == "__main__":
    main()
