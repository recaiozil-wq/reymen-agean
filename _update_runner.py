import sys

with open('reymen/ag/gateway_runner.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the DashboardChannel class to add DiscordChannel after it
dashboard_start = content.find('class DashboardChannel')
if dashboard_start < 0:
    print('ERROR: DashboardChannel not found')
    sys.exit(1)

# Find the next class or def after DashboardChannel
rest = content[dashboard_start:]
next_class = rest.find('\nclass ', 30)
next_def = rest.find('\ndef ', 30)
# Find the end of DashboardChannel class
# Look for the pattern of a blank line + comment line before next section
# Actually let's find the end of the DashboardChannel by looking for the last method's end
send_method = rest.find('async def send')
send_end = rest.find('\n        ', send_method + 20)
# Find the end of this class
class_end_search = rest[send_end:]
next_thing = class_end_search.find('\n\nclass ')
next_def2 = class_end_search.find('\n\ndef ')
next_hash = class_end_search.find('\n\n# ')
candidates = [x for x in [next_thing, next_def2, next_hash] if x > 0]
if candidates:
    end_offset = send_end + min(candidates)
else:
    end_offset = len(rest)

# Insert DiscordChannel class before the next section
insert_pos = dashboard_start + end_offset

discord_channel_code = """

class DiscordChannel(ChannelHandler):
    \"\"\"Discord kanali — discord_bot.py'yi alt surec olarak baslatir.\"\"\"

    def __init__(self):
        super().__init__("discord")
        self._process: Optional[subprocess.Popen] = None
        self._monitor_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        \"\"\"Discord bot'u subprocess olarak baslat.\"\"\"
        DISCORD_BOT_PATH = PROJE_KOK / "discord_bot.py"
        if not DISCORD_BOT_PATH.exists():
            self._status = "error"
            self._error = f"Discord bot bulunamadi: {DISCORD_BOT_PATH}"
            logger.error(f"[discord] {self._error}")
            return

        token = os.getenv("DISCORD_BOT_TOKEN", "")
        if not token:
            # .env'den dene
            env_path = PROJE_KOK / ".env"
            if env_path.exists():
                from dotenv import load_dotenv
                load_dotenv(env_path)
                token = os.getenv("DISCORD_BOT_TOKEN", "")

        if not token or token == "YOUR_DISCORD_BOT_TOKEN_HERE":
            self._status = "error"
            self._error = "DISCORD_BOT_TOKEN gecerli degil (placeholder)"
            logger.error(f"[discord] {self._error}")
            return

        try:
            self._process = subprocess.Popen(
                [sys.executable, str(DISCORD_BOT_PATH)],
                cwd=str(PROJE_KOK),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**os.environ, "DISCORD_BOT_TOKEN": token},
            )
            super().start()
            self._monitor_thread = threading.Thread(
                target=self._monitor_process,
                daemon=True,
                name="discord-monitor",
            )
            self._monitor_thread.start()
            logger.info("[discord] Bot sureci baslatildi (PID: %d)", self._process.pid)
        except Exception as e:
            self._status = "error"
            self._error = str(e)
            logger.error(f"[discord] Baslatma hatasi: {e}")

    def stop(self) -> None:
        \"\"\"Discord bot surecini durdur.\"\"\"
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=2)
            logger.info("[discord] Bot sureci sonlandirildi")
        super().stop()

    def send(self, message: str) -> None:
        \"\"\"Discord kanalina mesaj gonder (log'a yaz, bot.py yonetsin).\"\"\"
        if not self._running:
            return
        logger.info(f"[discord] Gonderilecek mesaj (bot.py yonetir): {message[:60]}...")

    def _monitor_process(self) -> None:
        \"\"\"Bot surecini izle, cokerse durumu guncelle.\"\"\"
        try:
            stdout, stderr = self._process.communicate()
            if self._running:
                logger.warning(
                    "[discord] Bot sureci beklenmedik sekilde sonlandi.\n"
                    f"  stdout: {stdout[-200:] if stdout else ''}\n"
                    f"  stderr: {stderr[-200:] if stderr else ''}"
                )
                self._status = "error"
                self._error = f"Process exited: {stderr[-200:] if stderr else 'unknown'}"
        except Exception as e:
            logger.error(f"[discord] Monitor hatasi: {e}")

"""

content = content[:insert_pos] + discord_channel_code + content[insert_pos:]

# Update create_default_gateway to include discord channel
old_default = """    gr.register_channel("dashboard", DashboardChannel())
    return gr"""

new_default = """    gr.register_channel("dashboard", DashboardChannel())
    gr.register_channel("discord", DiscordChannel())
    return gr"""

content = content.replace(old_default, new_default)

with open('reymen/ag/gateway_runner.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ gateway_runner.py: DiscordChannel eklendi, create_default_gateway() guncellendi.")
