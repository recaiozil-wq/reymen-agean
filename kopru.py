# -*- coding: utf-8 -*-
"""
kopru.py — Telegram Bridge (Bot1/Bot2)
========================================
ReYMeN (Bot1) ile ReYMeN (Bot2) arasinda mesaj koprusu.
Sadece ReYMeN botu poll edilir, ReYMeN botu sadece sendMessage yapar.
Boylece 409 Conflict onlenmis olur.

Kullanim:
  python kopru.py                   (bagimsiz script)
  Eylem: KOPRU_BASLAT()             (ReYMeN motorundan)

.env:
  BRIDGE_BOT1_TOKEN           ReYMeN bot token (poll edilen)
  BRIDGE_BOT1_TARGET_CHAT     ReYMeN botunun dinledigi chat
  BRIDGE_BOT2_TOKEN           ReYMeN bot token (sadece sendMessage)
  BRIDGE_BOT2_TARGET_CHAT     ReYMeN botunun yazacagi chat (TARGET)
"""

import asyncio
import logging
import os
import subprocess
import sys
import threading
from pathlib import Path
import logging
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# .env YUKLEYICI
# ─────────────────────────────────────────────


def load_dotenv(paths: list) -> None:
    """Birden fazla .env dosyasini tara, degiskenleri os.environ'a ekle."""
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        with open(p, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip("\"'")
                if key.startswith("BRIDGE_") or key.startswith("TELEGRAM_") or key.startswith("BOT_"):
                    os.environ.setdefault(key, val)


ENV_PATHS = [
    os.environ.get("LOCALAPPDATA", "") + "/hermes/.env",
    str(Path.home()) + "/AppData/Local/hermes/.env",
    str(Path.home()) + "/AppData/Local/ReYMeN/.env",
]
load_dotenv(ENV_PATHS)

# ─────────────────────────────────────────────
# AYARLAR - .env'den
# ─────────────────────────────────────────────

# ReYMeN botu - SADECE BU POLL EDILIR
BOT1_TOKEN = os.environ.get("BRIDGE_BOT1_TOKEN", "")
BOT1_TARGET_CHAT = int(os.environ.get("BRIDGE_BOT1_TARGET_CHAT", "0"))

# ReYMeN botu - POLL EDILMEZ, sadece sendMessage
BOT2_TOKEN = os.environ.get("BRIDGE_BOT2_TOKEN", "")
BOT2_TARGET_CHAT = int(os.environ.get("BRIDGE_BOT2_TARGET_CHAT", "0"))

# ─────────────────────────────────────────────
# LOG
# ─────────────────────────────────────────────

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bridge.log", encoding="utf-8"),
    ]
)
log = logging.getLogger("Kopru")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

# Arka plan thread kontrolu
_kopru_thread = None
_kopru_durdu = threading.Event()

# ─────────────────────────────────────────────
# WEBHOOK TEMIZLE
# ─────────────────────────────────────────────


async def clear_webhooks() -> None:
    """Her baslatmada Telegram tarafindaki kilidi sifirla."""
    try:
        from telegram import Bot
        from telegram.error import TelegramError
    except ImportError:
        log.error("python-telegram-bot kurulu degil. 'pip install python-telegram-bot'")
        return
    for name, token in [("ReYMeN bot", BOT1_TOKEN)]:
        try:
            bot = Bot(token)
            await bot.delete_webhook(drop_pending_updates=True)
            await bot.close()
            log.info(f"{name} webhook + close tamam.")
        except TelegramError as e:
            log.error(f"{name} temizleme hatasi: {e}")

# ─────────────────────────────────────────────
# MESAJ HANDLER - TEK YON
# ─────────────────────────────────────────────


async def on_message(update, context) -> None:
    """ReYMeN botuna gelen mesaji ReYMeN chat'ine ilet."""
    try:
        from telegram import Bot
        from telegram.error import TelegramError
    except ImportError:
        log.error("python-telegram-bot kurulu degil.")
        return

    msg = update.message
    if not msg or not msg.text:
        return
    if msg.from_user and msg.from_user.is_bot:
        return

    sender = msg.from_user.full_name if msg.from_user else "Bilinmeyen"
    text = f"[ReYMeN ← {sender}]\n{msg.text}"

    try:
        reymen_bot = Bot(BOT2_TOKEN)
        await reymen_bot.send_message(chat_id=BOT2_TARGET_CHAT, text=text)
        log.info(f"Iletildi: {msg.text[:50]}")
    except TelegramError as e:
        log.error(f"Iletim hatasi: {e}")

# ─────────────────────────────────────────────
# HATA YAKALAYICI
# ─────────────────────────────────────────────


async def error_handler(update, context) -> None:
    try:
        from telegram.error import Conflict
    except ImportError:
        log.error(f"Telegram hatasi: {context.error}")
        return
    if isinstance(context.error, Conflict):
        log.critical("409 Conflict: ReYMeN botu baska bir yerde poll ediliyor olabilir.")
    else:
        log.error(f"Telegram hatasi: {context.error}")

# ─────────────────────────────────────────────
# ANA DONGU
# ─────────────────────────────────────────────


async def bridge_main() -> None:
    """Bridge ana dongusu - asyncio ile calisir."""
    try:
        from telegram import Bot
        from telegram.ext import Application, MessageHandler, filters, ContextTypes
        from telegram.error import Conflict
    except ImportError as e:
        log.error(f"python-telegram-bot kurulu degil: {e}")
        return

    log.info("=" * 50)
    log.info("Telegram Bridge baslatiliyor...")
    log.info(f"Poll: ReYMeN botu → Hedef: {BOT2_TARGET_CHAT}")
    log.info("ReYMeN botu POLL EDILMEZ - sadece sendMessage")
    log.info("=" * 50)

    # Webhook temizle
    await clear_webhooks()
    await asyncio.sleep(3)

    app = Application.builder().token(BOT1_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
    app.add_error_handler(error_handler)

    async with app:
        await app.start()
        await app.updater.start_polling(
            drop_pending_updates=True,
            allowed_updates=["message"]
        )
        log.info("Bridge aktif - ReYMeN botu dinleniyor")
        log.info("Durdurmak icin Ctrl+C")

        try:
            await _kopru_durdu.wait()
        except (KeyboardInterrupt, asyncio.CancelledError) as _kopru_e197:
            print(f"[UYARI] kopru.py:198 - {_kopru_e197}")

        log.info("Polling durduruluyor...")
        await app.updater.stop()
        await app.stop()

    log.info("Bridge kapatildi.")

# ─────────────────────────────────────────────
# ARKAPLAN / THREAD API
# ─────────────────────────────────────────────


def kopru_baslat() -> str:
    """Bridge'i arka planda baslat. Thread olarak calisir."""
    global _kopru_thread

    if _kopru_thread and _kopru_thread.is_alive():
        return "[KOPRU] Zaten calisiyor."

    if not BOT1_TOKEN or not BOT2_TOKEN or BOT2_TARGET_CHAT == 0:
        return ("[KOPRU] Eksik .env ayarlari:\n"
                "  BRIDGE_BOT1_TOKEN, BRIDGE_BOT2_TOKEN, "
                "BRIDGE_BOT2_TARGET_CHAT gerekli")

    _kopru_durdu.clear()

    def _run():
        try:
            asyncio.run(bridge_main())
        except Exception as e:
            log.error(f"Bridge hatasi: {e}")

    _kopru_thread = threading.Thread(target=_run, daemon=True)
    _kopru_thread.start()
    return ("[KOPRU] Bridge baslatildi (arka planda).\n"
            f"  Poll: ReYMeN botu → ReYMeN chat ({BOT2_TARGET_CHAT})\n"
            "  Log: bridge.log")


def kopru_durdur() -> str:
    """Bridge'i durdur."""
    global _kopru_thread
    if not _kopru_thread or not _kopru_thread.is_alive():
        return "[KOPRU] Zaten calismiyor."
    _kopru_durdu.set()
    _kopru_thread.join(timeout=10)
    _kopru_thread = None
    return "[KOPRU] Bridge durduruldu."


def kopru_durum() -> str:
    """Bridge durumunu sorgula."""
    global _kopru_thread
    if _kopru_thread and _kopru_thread.is_alive():
        return ("[KOPRU] Calisiyor.\n"
                f"  Bot1 (poll): {BOT1_TOKEN[:8]}...\n"
                f"  Bot2 (send): {BOT2_TOKEN[:8]}...\n"
                f"  Hedef chat: {BOT2_TARGET_CHAT}")
    return "[KOPRU] Calismiyor."


# ── .kopru/ klasör tabanlı görev alışverişi (bot.py watcher için) ──

_KOPRU_KLASOR = Path(__file__).parent / ".kopru"


def kopru_gorevleri_tara() -> list:
    """.kopru/ klasorundeki JSON gorev dosyalarini tara ve listele."""
    import json
    if not _KOPRU_KLASOR.exists():
        return []
    gorevler = []
    try:
        for dosya in sorted(_KOPRU_KLASOR.glob("gorev_*.json")):
            try:
                data = json.loads(dosya.read_text(encoding="utf-8"))
                data["_dosya"] = str(dosya)
                gorevler.append(data)
            except (json.JSONDecodeError, OSError):
                continue
    except OSError as _kopru_e279:
        print(f"[UYARI] kopru.py:280 - {_kopru_e279}")
    return gorevler


def kopru_sonuc_yaz(gorev_id: str, sonuc: str) -> None:
    """.kopru/ klasorune sonuc JSON dosyasi yaz."""
    import json
    _KOPRU_KLASOR.mkdir(parents=True, exist_ok=True)
    dosya = _KOPRU_KLASOR / f"sonuc_{gorev_id}.json"
    dosya.write_text(
        json.dumps({"id": gorev_id, "sonuc": sonuc}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def kopru_gorev_sil(gorev_id: str) -> None:
    """.kopru/ klasorundeki gorev dosyasini sil."""
    for dosya in _KOPRU_KLASOR.glob(f"gorev_{gorev_id}.json"):
        try:
            dosya.unlink(missing_ok=True)
        except OSError as _kopru_e300:
            print(f"[UYARI] kopru.py:301 - {_kopru_e300}")


# ── MOTOR KAYIT (ReYMeN Motor entegrasyonu) ──


def motor_kaydet(motor) -> None:
    """ReYMeN motoruna KOPRU_BASLAT, KOPRU_DURDUR, KOPRU_DURUM araclarini kaydet."""
    motor._plugin_arac_kaydet(
        "KOPRU_BASLAT",
        kopru_baslat,
        "Telegram Bridge'i baslat (Bot1/Bot2). "
        "ReYMeN botu -> ReYMeN botu mesaj iletimi. "
        "On kosul: .env'de BRIDGE_BOT1_TOKEN, BRIDGE_BOT2_TOKEN, BRIDGE_BOT2_TARGET_CHAT",
    )
    motor._plugin_arac_kaydet(
        "KOPRU_DURDUR",
        kopru_durdur,
        "Telegram Bridge'i durdur.",
    )
    motor._plugin_arac_kaydet(
        "KOPRU_DURUM",
        kopru_durum,
        "Telegram Bridge durumunu sorgula.",
    )


# ─────────────────────────────────────────────
# BAGIMSIZ CALISTIRMA
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if not BOT1_TOKEN or not BOT2_TOKEN or BOT2_TARGET_CHAT == 0:
        log.error("Eksik .env ayari: BRIDGE_BOT1_TOKEN, BRIDGE_BOT2_TOKEN, BRIDGE_BOT2_TARGET_CHAT gerekli")
        sys.exit(1)
    try:
        asyncio.run(bridge_main())
    except KeyboardInterrupt:
        print("\nKapatildi.")
