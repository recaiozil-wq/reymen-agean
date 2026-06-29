import re
import sys

with open('reymen/ag/platform_gateways.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of DiscordGateway class
start = content.find('class DiscordGateway')
if start < 0:
    print('ERROR: DiscordGateway not found')
    sys.exit(1)

# Find the end - look for next class or def at module level after this class
rest = content[start:]
next_class = rest.find('\nclass ', 10)
next_def = rest.find('\ndef ', 10)
candidates = [x for x in [next_class, next_def] if x > 0]
if candidates:
    end = start + min(candidates)
else:
    end = len(content)

old = content[start:end]

new = """class DiscordGateway(GatewayBase):
    \"\"\"
    Discord platform gateway'i — REST API uzerinden mesaj gonderimi.

    discord.py ile bagimsiz calisir.
    Mesaj gondermek icin REST API kullanir (bot process'inden bagimsiz).
    \"\"\"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("discord", config)
        self._token: Optional[str] = None
        self._gelen_kuyruk: asyncio.Queue = asyncio.Queue()

    async def connect(self) -> bool:
        \"\"\"Discord API'sine baglan (token dogrulama).\"\"\"
        try:
            token = self._config.get("token") or os.getenv("DISCORD_BOT_TOKEN", "")
            if not token or token in ("", "YOUR_DISCORD_BOT_TOKEN_HERE"):
                self._son_hata = "DISCORD_BOT_TOKEN gecerli degil"
                logger.warning(f"[DiscordGateway] {self._son_hata}")
                self._bagli = False
                return False

            self._token = token
            self._bagli = True
            logger.info("[DiscordGateway] Discord baglantisi hazir (REST).")
            return True

        except Exception as e:
            self._son_hata = str(e)
            logger.error(f"[DiscordGateway] Baglanti hatasi: {e}")
            return False

    async def disconnect(self) -> bool:
        \"\"\"Discord baglantisini kes.\"\"\"
        try:
            self._token = None
            self._bagli = False
            logger.info("[DiscordGateway] Discord baglantisi kesildi.")
            return True
        except Exception as e:
            self._son_hata = str(e)
            return False

    async def send(self, mesaj: str, hedef: Optional[str] = None,
                   meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        \"\"\"Discord kanalina mesaj gonder (REST API).\"\"\"
        try:
            if not self._bagli or not self._token:
                return {"basarili": False, "hata": "Baglanti yok"}

            kanal_id = hedef or self._config.get("varsayilan_kanal_id")
            if not kanal_id:
                return {"basarili": False, "hata": "kanal_id gerekli (hedef veya config'de)"}

            # REST API ile gonder
            import urllib.request
            import urllib.error

            url = f"https://discord.com/api/v10/channels/{kanal_id}/messages"
            data = json.dumps({"content": mesaj}).encode("utf-8")
            headers = {
                "Authorization": f"Bot {self._token}",
                "Content-Type": "application/json",
                "User-Agent": "DiscordBot (ReYMeN, 1.0)",
            }

            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp_data = json.loads(resp.read())
                self._mesaj_sayaci += 1
                return {
                    "basarili": True,
                    "platform": "discord",
                    "hedef": kanal_id,
                    "mesaj_id": resp_data.get("id", "?"),
                }

        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:200]
            return {"basarili": False, "hata": f"HTTP {e.code}: {body}"}
        except Exception as e:
            return {"basarili": False, "hata": str(e)}

    async def receive(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        \"\"\"Discord'dan gelen mesaji al (kuyruktan).\"\"\"
        try:
            mesaj = await asyncio.wait_for(self._gelen_kuyruk.get(), timeout=timeout)
            return mesaj
        except asyncio.TimeoutError:
            return None

    async def health_check(self) -> Dict[str, Any]:
        \"\"\"Discord baglanti sagligi.\"\"\"
        return {
            "durum": "saglikli" if self._bagli and self._token else "kopuk",
            "platform": "discord",
            "token_var": bool(self._token),
        }

    def mesaj_ekle(self, mesaj: Dict[str, Any]) -> None:
        \"\"\"Discord'dan gelen mesaji kuyruga ekle (bot tarafindan cagrilir).\"\"\"
        self._gelen_kuyruk.put_nowait(mesaj)

"""

content = content[:start] + new + content[end:]

with open('reymen/ag/platform_gateways.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ platform_gateways.py: DiscordGateway guncellendi (stub -> functional REST)")
