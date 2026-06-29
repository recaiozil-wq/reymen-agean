# -*- coding: utf-8 -*-
"""
discord_bot.py — ReYMeN Discord Botu (discord.py + AIAgentOrchestrator).

Telegram bot'u ile aynı ConversationLoop + Beyin + Motor altyapısını kullanır.

Komutlar:
  !ping        — Bot gecikmesi
  !help        — Yardım listesi
  !status      — Sistem durumu (LM Studio, beceriler, kanban)
  !run <hedef> — Ajana gorev ver (AIAgentOrchestrator ile)
  !cancel      — Aktif gorevi iptal et
  !beceriler   — Kristallesmis beceri listesi
  !logs        — Son gateway log satirlari

Kurulum (.env):
  DISCORD_BOT_TOKEN=xxxx
  DISCORD_ALLOWED_CHANNELS=123,456  (bos = her kanala acik)

Calistir:
  python discord_bot.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import discord
from discord.ext import commands

from dotenv import load_dotenv

# ── Ayarlar ──────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env", override=True)

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
ALLOWED_CHANNELS_STR = os.environ.get("DISCORD_ALLOWED_CHANNELS", "").strip()
ALLOWED_CHANNELS = set()
if ALLOWED_CHANNELS_STR:
    for c in ALLOWED_CHANNELS_STR.split(","):
        c = c.strip()
        if c:
            ALLOWED_CHANNELS.add(int(c))

logger = logging.getLogger("discord_bot")

# Durum dosyasi (process_manager ile iletisim)
STATUS_DOSYASI = ROOT / ".ReYMeN" / "discord_status.json"


def _durum_yaz(anahtar: str, deger: object) -> None:
    """Durum bilgisini JSON dosyasina yaz."""
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


# Aktif gorev kilidi (ayni anda 1 gorev)
_gorev_kilidi = threading.Lock()
_aktif_gorev: dict | None = None


# ── Bot Sinifi ────────────────────────────────────────────────────────────

class ReYMeNDiscordBot(commands.Bot):
    """ReYMeN Discord botu — ConversationLoop + Beyin + Motor ile."""

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
        await self.change_presence(activity=discord.Game(name="🧠 ReYMeN | !help"))
        # Baslangic bildirimi
        logger.info("🤖 ReYMeN Discord botu aktif. Komutlar: !help")

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        # Kanal bazli izin kontrolu
        if ALLOWED_CHANNELS and message.channel.id not in ALLOWED_CHANNELS:
            return
        await self.process_commands(message)


# ── Komutlar ─────────────────────────────────────────────────────────────

@commands.command(name="ping")
async def cmd_ping(ctx: commands.Context) -> None:
    """Bot canli mi kontrol et."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! `{latency}ms`")


@commands.command(name="help")
async def cmd_help(ctx: commands.Context) -> None:
    """Komut listesi."""
    yardim = (
        "**🤖 ReYMeN Discord Bot**\n"
        "`!ping` — Bot gecikmesi\n"
        "`!status` — Sistem durumu (LM Studio, beceriler, kanban)\n"
        "`!run <hedef>` — Ajana gorev ver\n"
        "`!cancel` — Aktif gorevi iptal et\n"
        "`!beceriler` — Kristallesmis beceriler\n"
        "`!logs` — Son gateway loglari\n"
        "`!help` — Bu mesaj\n"
    )
    await ctx.send(yardim)


@commands.command(name="status")
async def cmd_status(ctx: commands.Context) -> None:
    """Sistem durumu — LM Studio, beceriler, kanban."""
    satirlar = ["**📊 ReYMeN DURUM**\n"]

    # Bot bilgisi
    uptime = time.time() - bot._start_time
    saat = int(uptime // 3600)
    dk = int((uptime % 3600) // 60)
    satirlar.append(f"Bot: ✅ @{bot.bot_username} ({saat}s {dk}dk)")
    satirlar.append(f"Ping: {round(bot.latency * 1000)}ms")

    # LM Studio
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:1234/v1/models", timeout=2)
        satirlar.append("LM Studio: **AKTIF**")
    except Exception:
        satirlar.append("LM Studio: KAPALI")

    # Aktif gorev
    global _aktif_gorev
    if _aktif_gorev:
        satirlar.append(f"Aktif gorev: `{_aktif_gorev['hedef'][:60]}`")
    else:
        satirlar.append("Aktif gorev: yok")

    # Beceriler
    try:
        from reymen.cereyan.closed_learning_loop import ClosedLearningLoop
        n = ClosedLearningLoop().toplam_beceri_sayisi()
        satirlar.append(f"Beceriler: **{n}**")
    except Exception:
        satirlar.append("Beceriler: ?")

    # Kanban
    try:
        from reymen.arac.kanban_orchestrator import AdvancedKanbanOrchestrator
        ozet = AdvancedKanbanOrchestrator().ozet()
        toplam = ozet.get("toplam", 0)
        satirlar.append(f"Kanban: {toplam} gorev")
    except Exception:
        pass

    await ctx.send("\n".join(satirlar))


@commands.command(name="run")
async def cmd_run(ctx: commands.Context, *, hedef: str = "") -> None:
    """Ajana gorev ver — AIAgentOrchestrator ile."""
    cid = ctx.channel.id

    if not hedef.strip():
        await ctx.send("Kullanim: `!run <hedef>`\nOrnek: `!run Python dosyasi olustur`")
        return

    if not _gorev_kilidi.acquire(blocking=False):
        await ctx.send("Simdi baska bir gorev calisiyor. `!cancel` ile iptal et.")
        return

    await ctx.send(f"✅ Basladi: **{hedef[:100]}**")

    def _calistir():
        global _aktif_gorev
        iptal = threading.Event()
        _aktif_gorev = {"hedef": hedef, "iptal": iptal, "channel_id": cid}
        try:
            from reymen.sistem.main import AIAgentOrchestrator, CONFIG
            agent = AIAgentOrchestrator(config=CONFIG, max_tur=20, onay_iste=False)

            sonuc_listesi = [None]
            hata_listesi = [None]

            def _run_thread():
                try:
                    sonuc_listesi[0] = agent.run_conversation(hedef)
                except Exception as e:
                    hata_listesi[0] = str(e)

            t = threading.Thread(target=_run_thread, daemon=True)
            t.start()

            # Iptal kontrolu (5 saniyede bir)
            while t.is_alive():
                if iptal.is_set():
                    asyncio.run_coroutine_threadsafe(
                        ctx.send("Gorev iptal edildi."), bot.loop
                    )
                    return
                time.sleep(5)

            if hata_listesi[0]:
                asyncio.run_coroutine_threadsafe(
                    ctx.send(f"HATA:\n{hata_listesi[0][:500]}"), bot.loop
                )
            else:
                sonuc = sonuc_listesi[0] or "(tamamlandi, cikti yok)"
                asyncio.run_coroutine_threadsafe(
                    ctx.send(f"**Sonuc:**\n{str(sonuc)[:2000]}"), bot.loop
                )

        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                ctx.send(f"Ajan baslatilamadi: {e}"), bot.loop
            )
        finally:
            _aktif_gorev = None
            _gorev_kilidi.release()

    threading.Thread(target=_calistir, daemon=True).start()


@commands.command(name="cancel")
async def cmd_cancel(ctx: commands.Context) -> None:
    """Aktif gorevi iptal et."""
    global _aktif_gorev
    if _aktif_gorev:
        _aktif_gorev["iptal"].set()
        await ctx.send(f"🛑 Iptal istegi gonderildi: `{_aktif_gorev['hedef'][:80]}`")
    else:
        await ctx.send("Aktif gorev yok.")


@commands.command(name="beceriler")
async def cmd_beceriler(ctx: commands.Context) -> None:
    """Kristallesmis beceri listesi."""
    try:
        from reymen.cereyan.closed_learning_loop import ClosedLearningLoop
        beceriler = ClosedLearningLoop().tum_beceriler()
        if not beceriler:
            await ctx.send("Hic beceri yok.")
            return
        satirlar = [f"**Beceriler ({len(beceriler)}):**"]
        for b in beceriler[:20]:
            satirlar.append(f"  • {b['ad']}: {b['aciklama'][:60]}")
        if len(beceriler) > 20:
            satirlar.append(f"  ... ve {len(beceriler)-20} tane daha")
        await ctx.send("\n".join(satirlar))
    except Exception as e:
        await ctx.send(f"Beceri hatasi: {e}")


@commands.command(name="logs")
async def cmd_logs(ctx: commands.Context) -> None:
    """Son gateway log satirlari."""
    log_dosyasi = ROOT / "logs" / "gateway.jsonl"
    if not log_dosyasi.exists():
        await ctx.send("Log dosyasi henuz olusturulmamis.")
        return
    try:
        with open(log_dosyasi, encoding="utf-8") as f:
            satirlar = f.readlines()
        son = satirlar[-15:]
        cikti_satirlari = []
        for s in son:
            try:
                e = json.loads(s)
                ts = e.get("timestamp", "")[:16]
                tip = e.get("type", "")
                msg_ = e.get("message", "")[:80]
                cikti_satirlari.append(f"[{ts}] {tip}: {msg_}")
            except Exception:
                cikti_satirlari.append(s.strip()[:100])
        await ctx.send("**GATEWAY LOG (son 15):**\n" + "\n".join(cikti_satirlari))
    except Exception as e:
        await ctx.send(f"Log okuma hatasi: {e}")


# ── Komutlari Kaydet ────────────────────────────────────────────────────

bot = ReYMeNDiscordBot()
bot.add_command(cmd_ping)
bot.add_command(cmd_help)
bot.add_command(cmd_status)
bot.add_command(cmd_run)
bot.add_command(cmd_cancel)
bot.add_command(cmd_beceriler)
bot.add_command(cmd_logs)


# ── Motor Entegrasyonu ──────────────────────────────────────────────────

def motor_bildirim_gonder(mesaj: str, kanal_id: str | None = None) -> str:
    """motor.py'den dogrudan Discord bildirimi gonder (REST API ile)."""
    if not TOKEN or TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        return "[Discord] Token ayarli degil."
    sonuc = send_rest_message(TOKEN, kanal_id or "", mesaj)
    if sonuc.get("ok"):
        return "[Discord] Gonderildi."
    return f"[Discord] Hata: {sonuc.get('hata', 'bilinmiyor')}"


def motor_kaydet(motor) -> None:
    """Motor'a DISCORD_GONDER aracini ekle."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "DISCORD_GONDER",
        lambda metin="", kanal_id="": motor_bildirim_gonder(metin, kanal_id or None),
        "Discord kanalina mesaj gonder (metin, kanal_id: opsiyonel)",
    )
    logger.info("[DiscordBot] DISCORD_GONDER araci kayit edildi.")


# ── REST API ile Mesaj Gonderme (Web UI / Motor kullanir) ───────────────

def send_rest_message(token: str, kanal_id: str, metin: str) -> dict:
    """Discord REST API uzerinden mesaj gonder.

    Bot process'inden bagimsiz calisir.
    Web UI / Motor bu fonksiyonu kullanarak bot kapaliyken de mesaj gonderebilir.
    """
    import urllib.request
    import urllib.error

    if not kanal_id:
        return {"ok": False, "hata": "kanal_id gerekli"}

    url = f"https://discord.com/api/v10/channels/{kanal_id}/messages"
    data = json.dumps({"content": metin}).encode("utf-8")
    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (ReYMeN, 1.0)",
    }

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp_data = json.loads(resp.read())
            return {"ok": True, "mesaj_id": resp_data.get("id", "?")}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:200]
        return {"ok": False, "hata": f"HTTP {e.code}: {body}"}
    except Exception as e:
        return {"ok": False, "hata": str(e)}


# ── Baslatma ────────────────────────────────────────────────────────────

def main() -> None:
    """Bot'u baslat."""
    if not TOKEN or TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        logger.error("❌ DISCORD_BOT_TOKEN .env'de ayarlanmamis")
        _durum_yaz("durum", "hata: token yok")
        print("[DiscordBot] ❌ DISCORD_BOT_TOKEN ayarli degil — .env'yi kontrol et.")
        sys.exit(1)

    _durum_yaz("durum", "basliyor")
    logger.info("🤖 ReYMeN Discord botu baslatiliyor...")
    print("[DiscordBot] 🤖 ReYMeN Discord botu baslatiliyor...")

    try:
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure:
        logger.error("❌ Discord giris basarisiz — token hatali")
        _durum_yaz("durum", "hata: giris basarisiz")
        sys.exit(1)
    except Exception as e:
        logger.error("❌ Discord bot hatasi: %s", e)
        _durum_yaz("durum", f"hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
