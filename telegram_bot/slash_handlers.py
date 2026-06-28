"""
telegram_bot/slash_handlers.py — ReYMeN Gelişmiş Slash Komutları.

ReYMeN gateway/slash_commands.py referans alınarak ReYMeN bot.py'ye
entegre edilmek üzere sadeleştirilmiştir.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger("reymen_bot.slash")

_BOT_ROOT = Path(__file__).parent.parent.resolve()
DATA_DIR = _BOT_ROOT / ".ReYMeN" / "telegram"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Veri yonetimi (bot.py'dekiyle ayni pattern) ──

def _sohbetleri_yukle() -> dict:
    path = DATA_DIR / "sohbetler.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def _sohbetleri_kaydet(sohbetler: dict):
    (DATA_DIR / "sohbetler.json").write_text(
        json.dumps(sohbetler, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )

def _sohbet_gecmisi_al(chat_id: str) -> list:
    return _sohbetleri_yukle().get(str(chat_id), [])

def _sohbet_gecmisi_guncelle(chat_id: str, mesajlar: list):
    sohbetler = _sohbetleri_yukle()
    sohbetler[str(chat_id)] = mesajlar
    _sohbetleri_kaydet(sohbetler)

# ── Handler'lar ──

async def gecmis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sohbet gecmisini goster (/gecmis)."""
    chat_id = str(update.effective_chat.id)
    mesajlar = _sohbet_gecmisi_al(chat_id)
    if not mesajlar:
        await update.message.reply_text("Henuz mesaj yok.")
        return
    # Son 10 mesaji ozetle
    ozet = []
    for m in mesajlar[-10:]:
        role = "🧑" if m.get("role") == "user" else "🤖"
        icerik = m.get("content", "")[:80]
        ozet.append(f"{role} {icerik}")
    await update.message.reply_text(
        f"📜 *Sohbet Gecmisi* (son {len(ozet)} mesaj)\\n\\n"
        + "\\n".join(ozet)
        + f"\\n\\nToplam: {len(mesajlar)} mesaj",
        parse_mode="Markdown",
    )


async def istatistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kullanim istatistiklerini goster (/istatistik)."""
    sohbetler = _sohbetleri_yukle()
    toplam_sohbet = len(sohbetler)
    toplam_mesaj = sum(len(m) for m in sohbetler.values())
    await update.message.reply_text(
        f"📊 *ReYMeN Istatistikleri*\\n\\n"
        f"Aktif sohbet: {toplam_sohbet}\\n"
        f"Toplam mesaj: {toplam_mesaj}\\n"
        f"Model: deepseek-chat\\n"
        f"Dil: Turkce",
        parse_mode="Markdown",
    )


async def kaydet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Konusmayi JSON olarak disa aktar (/kaydet)."""
    chat_id = str(update.effective_chat.id)
    mesajlar = _sohbet_gecmisi_al(chat_id)
    if not mesajlar:
        await update.message.reply_text("Kaydedilecek mesaj yok.")
        return
    # Dosyaya yaz
    export_dir = DATA_DIR / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    fname = f"sohbet_{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = export_dir / fname
    path.write_text(json.dumps(mesajlar, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    await update.message.reply_text(
        f"💾 *Sohbet Kaydedildi*\\n\\n"
        f"{len(mesajlar)} mesaj -> `{fname}`",
        parse_mode="Markdown",
    )


async def model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mevcut model bilgisini goster (/model)."""
    await update.message.reply_text(
        "🧠 *Model Bilgisi*\\n\\n"
        f"Suan: `deepseek-chat` (DeepSeek V3)\\n"
        f"API: {'✅ Bagli' if os.getenv('DEEPSEEK_API_KEY') else '❌ Anahtar yok'}\\n\\n"
        "Not: ReYMeN su an icin DeepSeek API ile calisir.",
        parse_mode="Markdown",
    )


async def temizle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Konusma gecmisini ve hafizayi temizle (/temizle)."""
    chat_id = str(update.effective_chat.id)
    _sohbet_gecmisi_guncelle(chat_id, [])
    await update.message.reply_text(
        "🗑️ *Sohbet temizlendi.*\\n\\n"
        "Hafiza sifirlandi, yeni bir konusmaya baslayabilirsin.",
        parse_mode="Markdown",
    )
