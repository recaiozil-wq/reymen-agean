import re
import os
import time
import subprocess
import sys
from pyrogram import Client
import logging

logger = logging.getLogger(__name__)

# ============ SADECE BUNLARI DOLDUR ============
API_ID = 12345678  # my.telegram.org'dan al
API_HASH = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
BOT_USERNAME = "ReYMeN_ReYMeNbot"  # @ olmadan bot kullanıcı adı
# =================================================

TOKEN_PATTERN = re.compile(r"\d+:[A-Za-z0-9_-]{35}")
SEARCH_ROOT = r"C:\Users\marko"


def find_bot_py():
    print("[1/6] bot.py dosyası aranıyor...")
    for root, dirs, files in os.walk(SEARCH_ROOT):
        # gereksiz yere derine inmesin diye bazı klasörleri atla
        dirs[:] = [
            d
            for d in dirs
            if d not in ("AppData", "node_modules", ".git", "venv", "__pycache__")
        ]
        if "bot.py" in files:
            path = os.path.join(root, "bot.py")
            print("    Bulundu:", path)
            return path
    raise FileNotFoundError("bot.py hiçbir yerde bulunamadı.")


def kill_existing_python():
    print("[2/6] Lokal python süreçleri kapatılıyor...")
    subprocess.run(
        [
            "powershell",
            "-Command",
            "Stop-Process -Name python -Force -ErrorAction SilentlyContinue",
        ],
        check=False,
    )
    time.sleep(1)


def revoke_and_get_new_token(app: Client) -> str:
    print("[3/6] BotFather ile token yenileniyor...")

    app.send_message("BotFather", "/mybots")
    time.sleep(2)
    msg = next(app.get_chat_history("BotFather", limit=1))
    msg.click(BOT_USERNAME)
    time.sleep(2)

    msg = next(app.get_chat_history("BotFather", limit=1))
    msg.click("API Token")
    time.sleep(2)

    msg = next(app.get_chat_history("BotFather", limit=1))
    msg.click("Revoke current token")
    time.sleep(2)

    msg = next(app.get_chat_history("BotFather", limit=1))
    match = TOKEN_PATTERN.search(msg.text or "")
    if not match:
        raise RuntimeError("Yeni token bulunamadı. Son mesaj:\n" + str(msg.text))
    return match.group(0)


def update_bot_py(bot_py_path: str, new_token: str):
    print("[4/6] bot.py içindeki token güncelleniyor...")
    with open(bot_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    old_match = TOKEN_PATTERN.search(content)
    if not old_match:
        raise RuntimeError("bot.py içinde eski token bulunamadı.")

    content = content.replace(old_match.group(0), new_token)

    with open(bot_py_path, "w", encoding="utf-8") as f:
        f.write(content)


def restart_bot(bot_py_path: str):
    print("[5/6] Bot yeniden başlatılıyor...")
    bot_dir = os.path.dirname(bot_py_path)
    subprocess.Popen(
        ["python", bot_py_path],
        cwd=bot_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    time.sleep(2)
    print("[6/6] Tamamlandı. Bot ayrı bir pencerede çalışıyor.")


def main():
    bot_py_path = find_bot_py()
    kill_existing_python()

    app = Client("my_account", api_id=API_ID, api_hash=API_HASH)
    with app:
        new_token = revoke_and_get_new_token(app)
        print("Yeni token:", new_token)
        update_bot_py(bot_py_path, new_token)

    restart_bot(bot_py_path)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("HATA:", e)
        sys.exit(1)
