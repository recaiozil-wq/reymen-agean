# -*- coding: utf-8 -*-
"""🤖 ReYMeN Discord Botu — discord.py ile standalone bot.

Kullanım:
    python discord_bot.py

.env'de DISCORD_BOT_TOKEN gereklidir.
Komutlar:
  !status — sistem durumu
  !help   — yardım
  !ping   — pong
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Ayarlar
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("discord_bot")

# Discord token
TOKEN = ""
env_yolu = ROOT / ".env"
if env_yolu.exists():
    for satir in env_yolu.read_text(encoding="utf-8").splitlines():
        satir = satir.strip()
        if satir.startswith("DISCORD_BOT_TOKEN") and "=" in satir:
            TOKEN = satir.split("=", 1)[1].strip().strip('"').strip("'")
            break
# Hermes env fallback
if not TOKEN:
    hermes_env = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / "kiral38" / ".env"
    if hermes_env.exists():
        for satir in hermes_env.read_text(encoding="utf-8").splitlines():
            satir = satir.strip()
            if satir.startswith("DISCORD_BOT_TOKEN") and "=" in satir:
                TOKEN = satir.split("=", 1)[1].strip().strip('"').strip("'")
                break
ALLOWED_CHANNELS = os.environ.get("DISCORD_ALLOWED_CHANNELS", "").strip()

# Durum dosyası (process_manager ile iletişim)
STATUS_DOSYASI = ROOT / ".ReYMeN" / "discord_status.json"


def _durum_yaz(anahtar: str, deger: object) -> None:
    """Durum bilgisini JSON dosyasına yaz."""
    STATUS_DOSYASI.parent.mkdir(parents=True, exist_ok=True)
    veri = {}
    if STATUS_DOSYASI.exists():
        try:
            veri = json.loads(STATUS_DOSYASI.read_text(encoding="utf-8"))
        except Exception:
            pass
    veri[anahtar] = deger
    veri["son_guncelleme"] = datetime.now().isoformat()
    STATUS_DOSYASI.write_text(json.dumps(veri, indent=2, ensure_ascii=False), encoding="utf-8")


try:
    import discord
    from discord.ext import commands
    HAS_DISCORD = True
except ImportError:
    HAS_DISCORD = False


# ── Bot ───────────────────────────────────────────────────────────────────


class ReYMeNDiscordBot(commands.Bot):
    """ReYMeN Discord botu."""

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents, help_command=None)
        self.bot_username: str = ""
        self._start_time: float = time.time()

    async def on_ready(self) -> None:
        self.bot_username = self.user.name if self.user else "?"
        logger.info("✅ Discord bot giris yapti: @%s", self.bot_username)
        _durum_yaz("bot_username", self.bot_username)
        _durum_yaz("durum", "calisiyor")
        _durum_yaz("giris_zamani", datetime.now().isoformat())

        # Bot durum mesajı
        await self.change_presence(
            activity=discord.Game(name="🧠 ReYMeN | !help")
        )

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        await self.process_commands(message)

    @commands.command(name="ping")
    async def cmd_ping(self, ctx: commands.Context) -> None:
        """Bot canlı mı kontrol et."""
        latency = round(self.latency * 1000)
        await ctx.send(f"🏓 Pong! `{latency}ms`")

    @commands.command(name="help")
    async def cmd_help(self, ctx: commands.Context) -> None:
        """Komut listesi."""
        yardim = (
            "**🤖 ReYMeN Discord Bot**\n"
            "`!ping` — Bot gecikmesi\n"
            "`!status` — Sistem durumu\n"
            "`!help` — Bu mesaj\n"
        )
        await ctx.send(yardim)

    @commands.command(name="status")
    async def cmd_status(self, ctx: commands.Context) -> None:
        """Sistem durumu."""
        uptime = time.time() - self._start_time
        saat = int(uptime // 3600)
        dk = int((uptime % 3600) // 60)
        await ctx.send(
            f"📊 **ReYMeN Durumu**\n"
            f"Bot: ✅ @{self.bot_username}\n"
            f"Çalışma: {saat}s {dk}dk\n"
            f"Ping: {round(self.latency * 1000)}ms\n"
        )


# ── Başlatma ──────────────────────────────────────────────────────────────


def main() -> None:
    """Bot'u başlat."""
    if not HAS_DISCORD:
        logger.error("❌ discord.py yuklu degil. 'pip install discord.py'")
        _durum_yaz("durum", "hata: discord.py yok")
        sys.exit(1)

    if not TOKEN:
        logger.error("❌ DISCORD_BOT_TOKEN .env'de bulunamadi")
        _durum_yaz("durum", "hata: token yok")
        sys.exit(1)

    _durum_yaz("durum", "basliyor")
    logger.info("🤖 ReYMeN Discord botu baslatiliyor...")

    bot = ReYMeNDiscordBot()

    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.error("❌ Discord giris basarisiz — token hatalı")
        _durum_yaz("durum", "hata: giris basarisiz")
        sys.exit(1)
    except Exception as e:
        logger.error("❌ Discord bot hatasi: %s", e)
        _durum_yaz("durum", f"hata: {e}")
        sys.exit(1)


# ── REST API ile mesaj gönderme (Web UI kullanır) ─────────────────────────


def send_rest_message(token: str, kanal_id: str, metin: str) -> dict:
    """discord.py HTTPClient ile REST üzerinden mesaj gönder.

    Bu fonksiyon bot process'inden bağımsız çalışır.
    Web UI bu fonksiyonu kullanarak bot kapalıyken de mesaj gönderebilir.
    """
    import requests

    url = f"https://discord.com/api/v10/channels/{kanal_id}/messages"
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
    }
    data = {"content": metin}

    resp = requests.post(url, headers=headers, json=data, timeout=10)
    if resp.status_code in (200, 201):
        return {"ok": True, "mesaj_id": resp.json().get("id", "?")}
    else:
        return {
            "ok": False,
            "hata": f"HTTP {resp.status_code}: {resp.text[:200]}",
        }


if __name__ == "__main__":
    main()
