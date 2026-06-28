"""
Telegram Bot Köprüsü — ReYMeN Cron Yöneticisi.

Komutlar:
  /run <job_name>   — Belirtilen job'ı çalıştırır
  /status           — Tüm job'ların durumunu listeler
  /logs <job_name>  — Belirtilen job'ın log çıktısını gösterir

Token .env dosyasından okunur (TELEGRAM_BOT_TOKEN).
"""

import json
import logging
import os
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ── Setup ───────────────────────────────────────────────────────────
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Data Store ──────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
JOBS_FILE = DATA_DIR / "jobs.json"
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)


def load_jobs() -> dict:
    if JOBS_FILE.exists():
        return json.loads(JOBS_FILE.read_text())
    return {}


def save_jobs(jobs: dict):
    JOBS_FILE.write_text(json.dumps(jobs, indent=2, default=str))


# ── Job Runner ──────────────────────────────────────────────────────
def run_shell_job(job_id: str, command: str):
    """Run shell command, write log, update status."""
    jobs = load_jobs()
    job = jobs.get(job_id, {})
    job["status"] = "running"
    job["started_at"] = datetime.now(timezone.utc).isoformat()
    save_jobs(jobs)

    log_file = LOGS_DIR / f"{job_id}.log"
    try:
        result = subprocess.run(
            command,
            shell=False,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        output = result.stdout + result.stderr
        log_file.write_text(output)

        jobs = load_jobs()
        job = jobs.get(job_id, {})
        job["status"] = "success" if result.returncode == 0 else "failed"
        job["exit_code"] = result.returncode
        job["finished_at"] = datetime.now(timezone.utc).isoformat()
        job["log"] = output
        save_jobs(jobs)
    except Exception as e:
        output = f"Error: {e}"
        log_file.write_text(output)
        jobs = load_jobs()
        job = jobs.get(job_id, {})
        job["status"] = "failed"
        job["finished_at"] = datetime.now(timezone.utc).isoformat()
        job["log"] = output
        save_jobs(jobs)


def add_job(name: str, command: str, schedule: str = "") -> str:
    """Register a job and run it in a background thread."""
    jobs = load_jobs()
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "id": job_id,
        "name": name,
        "command": command,
        "schedule": schedule,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    save_jobs(jobs)

    thread = threading.Thread(
        target=run_shell_job, args=(job_id, command), daemon=True
    )
    thread.start()
    return job_id


# ── Telegram Handlers ───────────────────────────────────────────────


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message."""
    await update.message.reply_text(
        "🤖 *ReYMeN Cron Bot*\n\n"
        "Komutlar:\n"
        "`/run <job_name>` — Job çalıştır\n"
        "`/status` — Tüm job'ları listele\n"
        "`/logs <job_name>` — Job log'larını göster\n"
        "`/help` — Yardım\n\n"
        "_Örnek: /run backup-db_",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


async def run_job(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Run a job by name. Usage: /run <job_name> <command>"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Kullanım:* `/run <job_name> <shell_command>`\n\n"
            "Örnek: `/run backup-db pg_dump -U postgres mydb`",
            parse_mode="Markdown",
        )
        return

    name = context.args[0]
    command = " ".join(context.args[1:]) if len(context.args) > 1 else name

    job_id = add_job(name, command)

    await update.message.reply_text(
        f"✅ *Job başlatıldı:* `{name}`\n"
        f"   └ ID: `{job_id}`\n"
        f"   └ Command: `{command[:100]}`\n\n"
        f"Durumu görmek için: `/status`\n"
        f"Log için: `/logs {name}`",
        parse_mode="Markdown",
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all jobs and their statuses."""
    jobs = load_jobs()

    if not jobs:
        await update.message.reply_text(
            "📭 *Hiç job bulunamadı.*\n"
            "Job eklemek için: `/run <name> <command>`",
            parse_mode="Markdown",
        )
        return

    lines = ["📊 *Job Durumları*\n"]
    for jid, job in sorted(
        jobs.items(), key=lambda x: x[1].get("created_at", ""), reverse=True
    ):
        name = job.get("name", jid)
        status_emoji = {
            "running": "🟢",
            "success": "✅",
            "failed": "❌",
            "pending": "⏳",
        }.get(job.get("status", ""), "⚪")
        status_text = job.get("status", "unknown")
        started = job.get("started_at", "")[:19] if job.get("started_at") else "-"

        lines.append(
            f"{status_emoji} *{name}*\n"
            f"   ├ Status: `{status_text}`\n"
            f"   └ Started: `{started}`"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show logs for a specific job. Usage: /logs <job_name>"""
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Kullanım:* `/logs <job_name>`\n\n"
            "Örnek: `/logs backup-db`",
            parse_mode="Markdown",
        )
        return

    job_name = " ".join(context.args).strip().lower()
    jobs = load_jobs()

    # Find job by name (case-insensitive)
    matched_job = None
    matched_id = None
    for jid, job in jobs.items():
        if job.get("name", "").strip().lower() == job_name:
            matched_job = job
            matched_id = jid
            break

    if not matched_job:
        # Try partial match
        for jid, job in jobs.items():
            if job_name in job.get("name", "").strip().lower():
                matched_job = job
                matched_id = jid
                break

    if not matched_job:
        await update.message.reply_text(
            f"❌ *Job bulunamadı:* `{job_name}`\n\n"
            f"Mevcut job'lar: `/status`",
            parse_mode="Markdown",
        )
        return

    log = matched_job.get("log", "")
    if not log:
        log_file = LOGS_DIR / f"{matched_id}.log"
        if log_file.exists():
            log = log_file.read_text()

    if not log:
        await update.message.reply_text(
            f"📭 *`{matched_job['name']}`* job'ı için henüz log yok.\n"
            f"   Status: `{matched_job.get('status', 'unknown')}`",
            parse_mode="Markdown",
        )
        return

    # Truncate if too long (Telegram max ~4096 chars)
    max_len = 3900
    if len(log) > max_len:
        log = log[:max_len] + "\n\n... (log truncated)"

    # Escape special characters for Markdown
    log_escaped = (
        log.replace("_", "\\_")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("`", "\\`")
    )

    await update.message.reply_text(
        f"📋 *Log: `{matched_job['name']}`*\n"
        f"   Status: `{matched_job.get('status', 'unknown')}`\n"
        f"```\n{log_escaped}\n```",
        parse_mode="Markdown",
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")


async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Normal mesajlara AI ile yanit ver. OnceHafiza'ya bakar, varsa direkt dondur."""
    if not update.message or not update.message.text:
        return
    metin = update.message.text.strip()
    if metin.startswith("/"):
        return  # Komutlari karistirma

    # ── OnceHafiza kontrolu ──────────────────────────────────────
    try:
        from pathlib import Path as _Path2
        _proje_kok2 = _Path2(__file__).parent.parent.resolve()
        import sys as _sys2
        if str(_proje_kok2) not in _sys2.path:
            _sys2.path.insert(0, str(_proje_kok2))
        from reymen.cereyan.once_hafiza import hafizada_ara, kaydet
        _hafiza = hafizada_ara(metin, kategori="")
        if _hafiza and _hafiza[0].get("guven", 0) > 0.7:
            _cevap = _hafiza[0].get("cozum", "")[:2000]
            if _cevap:
                await update.message.reply_text(f"🧠 {_cevap}")
                return
    except Exception:
        pass  # Hafiza yoksa normal akisa devam

    # Kullaniciya bekleme mesaji goster
    bekleme = await update.message.reply_text("Dusunuyorum...")

    try:
        # ReYMeN AI motoruna baglan
        import sys as _sys
        from pathlib import Path as _Path
        _proje_kok = _Path(__file__).parent.parent.resolve()
        if str(_proje_kok) not in _sys.path:
            _sys.path.insert(0, str(_proje_kok))

        # .env'den token oku
        from dotenv import load_dotenv
        load_dotenv(str(_proje_kok / ".env"))

        from beyin import Beyin as _Beyin
        import os as _os

        # ReYMeN config
        _cfg = {
            "default_provider": _os.environ.get("ReYMeN_DEFAULT_PROVIDER", "deepseek"),
            "default_model": _os.environ.get("ReYMeN_DEFAULT_MODEL", "deepseek-chat"),
            "providers": {
                "deepseek": {"base_url": "https://api.deepseek.com",
                             "api_key": _os.environ.get("DEEPSEEK_API_KEY", "")},
                "openrouter": {"base_url": "https://openrouter.ai/api/v1",
                               "api_key": _os.environ.get("OPENROUTER_API_KEY", "")},
            },
        }
        _beyin = _Beyin(_cfg)

        # AI'ya sor
        _sistem = "Sen ReYMeN adinda yardimsever bir AI asistanisin. Kisa ve oz cevap ver. Turkce konus."
        _yanit = _beyin.uret(_sistem, [{"role": "user", "content": metin}])
        _cevap = _yanit.strip() if _yanit else "Anlayamadim, tekrar dener misin?"

        # Cevabi hafizaya kaydet
        try:
            from reymen.cereyan.once_hafiza import kaydet as _kaydet
            _kaydet(metin, "bot_sohbet", _cevap, basari=True)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")

    except Exception as e:
        _cevap = f"Ufak bir aksaklik oldu: {str(e)[:100]}"
        logger.error(f"AI yanit hatasi: {e}")

    # Bekleme mesajini sil, gercek cevabi gonder
    try:
        await bekleme.delete()
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")
    await update.message.reply_text(_cevap[:2000])


async def bot_komutlarini_ayarla(app):
    """BotFather'a komut listesini kaydet."""
    try:
        await app.bot.set_my_commands([
            ("start", "Botu baslat / menu"),
            ("run", "Job calistir: /run <ad> <komut>"),
            ("status", "Job durumlarini listele"),
            ("logs", "Job logunu goster: /logs <ad>"),
            ("help", "Yardim"),
        ])
        logger.info("Komut listesi Telegram'a kaydedildi")
    except Exception as e:
        logger.warning(f"Komut listesi kaydedilemedi: {e}")


# ── Main ────────────────────────────────────────────────────────────
def main():
    """Start the Telegram bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN bulunamadı! "
            "Lütfen .env dosyasına TELEGRAM_BOT_TOKEN=... ekleyin."
        )
        sys.exit(1)

    app = Application.builder().token(token).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("run", run_job))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("logs", logs))

    # Normal mesaj handler (komut disi)
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("\U0001f916 ReYMeN Telegram Bot başlatılıyor...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
