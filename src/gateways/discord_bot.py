# -*- coding: utf-8 -*-
"""
discord_bot.py — ReYMeN Discord Botu (discord.py tabanli).

Telegram gateway (telegram_bot.py) ile ayni mantikta:
- discord.py (py-cord) ile Gateway ve mesaj altyapisi
- Beyin (LLM) + OnceHafiza + ConversationLoop entegrasyonu
- SOUL.md destegi
- Session yonetimi (her kanal/kullanici ayri session)
- Komutlar: /new, /stop, /retry, /model, /status
- Gateway yoneticisine kayit

Apache 2.0 Lisansi — github.com/NousResearch/hermes-agent
================================================
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sys
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

# ============================================================================
# PROJE KOKU & SYS.PATH
# ============================================================================
_PROJE_KOK = (
    Path(__file__).resolve().parent.parent.parent
)  # reymen/ag/../../ = proje koku
if str(_PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(_PROJE_KOK))
_SRC = _PROJE_KOK / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# ============================================================================
# LOGGER
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("discord_bot")

# ============================================================================
# GRACEFUL IMPORTLAR
# ============================================================================

# — Dotenv (.env yukleme) —
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# — discord.py —
DISCORD_AVAILABLE = False
try:
    import discord
    from discord.ext import commands

    DISCORD_AVAILABLE = True
except ImportError:
    discord = None
    commands = None

# — Beyin (LLM) —
BEYIN_CLS = None
try:
    from reymen.cereyan.beyin import Beyin as _B

    BEYIN_CLS = _B
except ImportError as e:
    logger.warning("Beyin import edilemedi: %s", e)

# — OnceHafiza —
ONCE_HAFIZA_ARA = None
ONCE_HAFIZA_KAYDET = None
try:
    from reymen.cereyan.once_hafiza import hafizada_ara as _ara, kaydet as _kaydet

    ONCE_HAFIZA_ARA = _ara
    ONCE_HAFIZA_KAYDET = _kaydet
except ImportError as e:
    logger.warning("OnceHafiza import edilemedi: %s", e)

# — ConversationLoop —
CONVERSATION_LOOP_CLS = None
try:
    from reymen.cereyan.conversation_loop import ConversationLoop as _CL

    CONVERSATION_LOOP_CLS = _CL
except ImportError as e:
    logger.warning("ConversationLoop import edilemedi: %s", e)

# — Ortak komutlar —
try:
    from reymen.ag.ortak_komutlar import (
        komut_isle as ortak_komut_isle,
        cmd_run as ortak_cmd_run,
    )
except ImportError:
    ortak_komut_isle = None
    ortak_cmd_run = None

# — Gateway yoneticisi (opsiyonel kayit) —
try:
    from reymen.ag.gateway_yonetici import GatewayManager
    from reymen.ag.platform_gateways import DiscordGateway

    GATEWAY_MANAGER_AVAILABLE = True
except ImportError:
    GatewayManager = None
    DiscordGateway = None
    GATEWAY_MANAGER_AVAILABLE = False

# ============================================================================
# CEVRESEL DEGISKENLER
# ============================================================================
_ENV_YUKLENDI = False


def _env_yukle():
    """.env dosyasini yukle (sadece 1 kere).

    Oncelik sirasi:
      1. Ortam degiskeni (bot_supervisor.py ile gelen DISCORD_BOT_TOKEN)
      2. Proje kokundeki .env
      3. Hermes profil .env'si (HERMES_PROFILE'a gore)
    """
    global _ENV_YUKLENDI
    if _ENV_YUKLENDI:
        return
    _ENV_YUKLENDI = True
    if load_dotenv is None:
        return

    # 1. Proje kokundeki .env (fallback)
    y = _PROJE_KOK / ".env"
    if y.exists():
        load_dotenv(str(y), override=False)
        logger.debug(".env fallback yuklendi: %s", y)

    # 2. Hermes profil .env
    profil = os.environ.get("HERMES_PROFILE", "reymen")
    hermes_env = (
        Path.home() / "AppData" / "Local" / "hermes" / "profiles" / profil / ".env"
    )
    if hermes_env.exists():
        load_dotenv(str(hermes_env), override=True)
        logger.info("Hermes profil .env yuklendi: %s (override=True)", hermes_env)


_env_yukle()

TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "").strip()
COMMAND_PREFIX = os.environ.get("DISCORD_COMMAND_PREFIX", "/")

# ============================================================================
# OTOMATIK DURUM GUNCELLEME
# ============================================================================
try:
    from reymen.sistem.ortak_komut import guncelle as durum_otomatik_guncelle
    from reymen.sistem.ortak_watchdog import watchdog_baslat

    durum_otomatik_guncelle()
    watchdog_baslat(interval=30)
except Exception as e:
    logger.debug("OrtakKomut yukleme hatasi (opsiyonel): %s", e)

# ============================================================================
# AKTIF GOREV KILIDI
# ============================================================================
_gorev_kilidi = threading.Lock()
_aktif_gorev: Optional[dict] = None


# ============================================================================
# YARDIMCI FONKSIYONLAR
# ============================================================================


def _durum_guncelle(bot_adi: str):
    """KATI KURAL: Her bot baslangicinda kendini durum.json'a ekler/gunceller."""
    try:
        from reymen.sistem.durum import degisiklik_ekle

        durum_yolu = _PROJE_KOK / "durum.json"
        if durum_yolu.exists():
            veri = json.loads(durum_yolu.read_text(encoding="utf-8"))
            botlar = veri.get("botlar", {})

            var = False
            for key, val in botlar.items():
                if isinstance(val, dict) and val.get("bot_adi", "") == bot_adi:
                    var = True
                    break

            if not var:
                anahtar = bot_adi.replace("@", "").replace("#", "").lower()
                botlar[anahtar] = {
                    "profil": os.environ.get("HERMES_PROFILE", "reymen"),
                    "bot_adi": bot_adi,
                    "gateway": "aktif",
                    "yetki": "tam",
                    "browser": "acik",
                    "terminal": "acik",
                    "web": "firecrawl",
                    "soul_boyut": 4799,
                    "tools": "tum",
                    "platform": "discord",
                }
                veri["botlar"] = botlar
                durum_yolu.write_text(
                    json.dumps(veri, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                logger.info("[%s] ✅ Yeni Discord bot durum.json'a eklendi!", bot_adi)
                degisiklik_ekle(bot_adi, f"Discord bot otomatik eklendi: {bot_adi}")
            else:
                logger.debug("[%s] durum.json'da zaten kayitli", bot_adi)
        else:
            logger.warning("[%s] durum.json bulunamadi!", bot_adi)
    except Exception as _e:
        logger.warning("[%s] _durum_guncelle hatasi: %s", bot_adi, _e)


# ============================================================================
# DISCORD BOT PROCESS — AI + OnceHafiza + ConversationLoop
# ============================================================================

_VARSAYILAN_AYARLAR = {
    "model": "deepseek-v4-flash",
    "provider": "deepseek",
    "sistem_prompt": None,
    "bilinen_kanallar": [],
    "konusma_gecmisi": [],
}


class DiscordBotProcess:
    """Tek bir Discord botu icin AI Agent Orchestrator.

    Telegram BotProcess ile ayni yapida:
    - discord.py (py-cord) ile Gateway
    - Beyin ile LLM yaniti uretir
    - OnceHafiza ile hafiza kontrolu
    - ConversationLoop ile tool kullanimi (opsiyonel)
    - Session yonetimi (her kanal/kullanici ayri session)
    - Komutlar: /new, /stop, /retry, /model, /status
    """

    def __init__(self, token: str, bot_ad: str = ""):
        _env_yukle()
        self.token = token
        self.bot_ad = bot_ad or self._bot_bilgisi_al()
        self.ayar_dosyasi = (
            _PROJE_KOK
            / ".ReYMeN"
            / f"discord_bot_{self.bot_ad.replace('@', '').replace('#', '')}.json"
        )
        self.ayarlar: dict = dict(_VARSAYILAN_AYARLAR)
        self._beyin = None
        self._loop = None
        self._bot: Optional[commands.Bot] = None
        self._gorevler: Dict[str, Any] = {}  # kanal_id -> aktif gorev

        self._ayar_yukle()
        self._beyin_baslat()
        _durum_guncelle(self.bot_ad)
        logger.info("[%s] DiscordBotProcess baslatildi", self.bot_ad)

    # ── Bot bilgisi ────────────────────────────────────────────────────

    def _bot_bilgisi_al(self) -> str:
        """Bot bilgisini .env'den veya geriye donuk olarak al."""
        # Discord botu baslayinca gercek adi bilinecek
        return os.environ.get("DISCORD_BOT_NAME", "ReYMeN-Discord")

    # ── Ayar yonetimi ──────────────────────────────────────────────────

    def _ayar_yukle(self):
        try:
            if self.ayar_dosyasi.exists():
                okunan = json.loads(self.ayar_dosyasi.read_text(encoding="utf-8"))
                self.ayarlar.update(okunan)
        except Exception as e:
            logger.warning("[%s] Ayar yukleme hatasi: %s", self.bot_ad, e)

    def _ayar_kaydet(self):
        try:
            self.ayar_dosyasi.parent.mkdir(parents=True, exist_ok=True)
            self.ayar_dosyasi.write_text(
                json.dumps(self.ayarlar, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error("[%s] Ayar kaydedilemedi: %s", self.bot_ad, e)

    def kanal_ekle(self, channel_id: int):
        kanallar = self.ayarlar.setdefault("bilinen_kanallar", [])
        if channel_id not in kanallar:
            kanallar.append(channel_id)
            self.ayarlar["bilinen_kanallar"] = kanallar
            self._ayar_kaydet()

    def konusma_ekle(
        self, session_id: str, kullanici: str, asistan: str, maks: int = 10
    ):
        sessionlar = self.ayarlar.setdefault("sessionlar", {})
        gecmis = sessionlar.setdefault(session_id, [])
        gecmis.append({"kullanici": kullanici, "asistan": asistan})
        if len(gecmis) > maks:
            sessionlar[session_id] = gecmis[-maks:]
        self.ayarlar["sessionlar"] = sessionlar
        self._ayar_kaydet()

    def session_gecmisi_al(self, session_id: str) -> list:
        return self.ayarlar.get("sessionlar", {}).get(session_id, [])

    def session_sifirla(self, session_id: str):
        sessionlar = self.ayarlar.setdefault("sessionlar", {})
        sessionlar[session_id] = []
        self.ayarlar["sessionlar"] = sessionlar
        self._ayar_kaydet()

    # ── Beyin baslat ──────────────────────────────────────────────────

    def _beyin_baslat(self):
        """Beyin + ConversationLoop baslat. SADECE deepseek-v4-flash."""
        if BEYIN_CLS is None:
            logger.warning("[%s] Beyin modulu yuklu degil!", self.bot_ad)
            return

        provider = "deepseek"
        model = "deepseek-v4-flash"
        self.ayarlar["provider"] = provider
        self.ayarlar["model"] = model

        deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
        openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")

        cfg = {
            "default_provider": provider,
            "default_model": model,
            "providers": {
                "deepseek": {
                    "base_url": "https://api.deepseek.com",
                    "api_key": deepseek_key,
                },
                "openrouter": {
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": openrouter_key,
                },
            },
        }
        try:
            self._beyin = BEYIN_CLS(cfg)
        except Exception as e:
            logger.error("[%s] Beyin baslatma hatasi: %s", self.bot_ad, e)
            return

        if CONVERSATION_LOOP_CLS is not None:
            try:
                self._loop = CONVERSATION_LOOP_CLS(
                    beyin=self._beyin, motor=None, max_tur=5
                )
            except Exception as e:
                logger.warning(
                    "[%s] ConversationLoop baslatma hatasi: %s", self.bot_ad, e
                )

        logger.info("[%s] Beyin aktif: %s / %s", self.bot_ad, provider, model)

    # ── TOOL: Web Arama ────────────────────────────────────────────────

    def _tool_web_search(self, sorgu: str) -> str:
        """Web'de ara ve sonucu metin olarak dondur."""
        import urllib.parse as _up
        import requests as _req
        import re as _re

        # 1. BING (en stabil)
        try:
            url = f"https://www.bing.com/search?q={_up.quote(sorgu)}&mkt=tr-TR"
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36"
            }
            r = _req.get(url, headers=headers, timeout=10)
            sonuc = " | ".join(
                _re.findall(
                    r'<li[^>]*class="b_algo"[^>]*>.*?<h2[^>]*>(.*?)</h2>',
                    r.text,
                    _re.DOTALL,
                )[:5]
            )
            if sonuc:
                sonuc = _re.sub(r"<[^>]+>", "", sonuc)
                sonuc = _re.sub(r"&#\d+;", "", sonuc)
                return sonuc.strip()
        except Exception as _e:
            logger.warning("[%s] Bing hatasi: %s", self.bot_ad, _e)

        # 2. DUCKDUCKGO FALLBACK
        try:
            url = f"https://html.duckduckgo.com/html/?q={_up.quote(sorgu)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            r = _req.get(url, headers=headers, timeout=10)
            sonuc = " ".join(
                _re.findall(r'<a[^>]*class="result__a"[^>]*>(.*?)</a>', r.text)[:5]
            )
            if sonuc:
                return sonuc
        except Exception as e:
            log.warning(f"[discord_bot] Web arama hatasi: {e}")
            pass

        return "(web arama su an kullanilamiyor)"

    # ── AI yanit uret ──────────────────────────────────────────────────

    def ai_yanit_uret(self, mesaj: str, session_id: Optional[str] = None) -> str:
        """OnceHafiza + Beyin ile yanit uret (30sn timeout).

        Args:
            mesaj: Kullanici mesaji
            session_id: Session ID (kanal_id veya kullanici_id)

        Returns:
            AI yaniti (en fazla 2000 karakter)
        """
        # 1. OnceHafiza kontrolu
        if ONCE_HAFIZA_ARA is not None:
            try:
                h = ONCE_HAFIZA_ARA(mesaj, kategori="")
                if h and len(h) > 0:
                    kayit = h[0] if isinstance(h[0], dict) else {}
                    guven = kayit.get("guven", 0) if isinstance(kayit, dict) else 0
                    if guven > 0.7:
                        cozum = (
                            kayit.get("cozum", "")
                            if isinstance(kayit, dict)
                            else (kayit[3] if len(kayit) > 3 else "")
                        )
                        if cozum:
                            return cozum[:2000]
            except Exception as _e:
                log.warning(f"[discord_bot] Cozum bulma hatasi: {_e}")
                pass

        # 2. Dogrudan Beyin (30sn timeout ile)
        if self._beyin is not None:
            sonuc = {"cevap": None}

            def _cagir():
                try:
                    self._ayar_yukle()
                    sistem = self.ayarlar.get("sistem_prompt", None)
                    if not sistem:
                        try:
                            _soul = _PROJE_KOK / "SOUL.md"
                            if _soul.exists():
                                sistem = _soul.read_text(encoding="utf-8")
                            else:
                                sistem = (
                                    "Sen ReYMeN adinda yardimsever bir AI asistanisin. "
                                    "Kisa ve oz cevap ver. Turkce konus."
                                )
                        except Exception:
                            sistem = (
                                "Sen ReYMeN adinda yardimsever bir AI asistanisin. "
                                "Kisa ve oz cevap ver. Turkce konus."
                            )

                    from datetime import date as _date

                    sistem += f"\n\n[TEMEL KURAL: ÖNCE BAK, SONRA KONUŞ]\n"
                    sistem += f"BUGUNUN TARIHI: {_date.today()}\n"
                    sistem += "1. Önce web'den araştır. Web sonucu varsa SADECE onu kullan, kendi ezberinden ASLA tahmin etme.\n"
                    sistem += "2. Web sonucu yoksa 'güncel veri alınamadı' de, kendi bilginle tahmin etme.\n"
                    sistem += "3. Sorunu analiz et, adım adım çözüm sun, alternatifleri belirt.\n"
                    sistem += (
                        "4. Selam/teşekkür gibi basit mesajlarda kısa cevap ver.\n"
                    )

                    # ── TOOL OTOMATIK CALISTIRMA ─────────────────────
                    _tool_cikti = ""
                    _mesaj_lower = mesaj.lower()

                    _soru_mi = (
                        "?" in mesaj
                        or "nedir" in _mesaj_lower
                        or "nasıl" in _mesaj_lower
                        or "ne" in _mesaj_lower
                        or "mi" in _mesaj_lower
                        or "kaç" in _mesaj_lower
                        or "neden" in _mesaj_lower
                        or len(mesaj.split()) >= 4
                    )
                    _selam_mi = _mesaj_lower.strip() in [
                        "merhaba",
                        "selam",
                        "hey",
                        "sa",
                        "hi",
                        "hello",
                        "iyi günler",
                    ]
                    if _soru_mi and not _selam_mi:
                        logger.info(
                            "[%s] 🔍 Web arama tetiklendi: %s", self.bot_ad, mesaj[:60]
                        )
                        _tool_cikti = self._tool_web_search(mesaj)
                        logger.info(
                            "[%s] 🔍 Web sonucu (%d karakter): %s",
                            self.bot_ad,
                            len(_tool_cikti),
                            _tool_cikti[:200],
                        )
                        sistem += f"\n\n🔍 WEB ARAMA SONUCU:\n{_tool_cikti}\n"

                    # ── Session gecmisi ──────────────────────────────
                    if session_id:
                        gecmis = self.session_gecmisi_al(session_id)
                    else:
                        gecmis = []

                    msg_list = []
                    for kayit in gecmis[-5:]:
                        if isinstance(kayit, dict):
                            if kayit.get("kullanici"):
                                msg_list.append(
                                    {"role": "user", "content": kayit["kullanici"]}
                                )
                            if kayit.get("asistan"):
                                msg_list.append(
                                    {"role": "assistant", "content": kayit["asistan"]}
                                )
                    msg_list.append({"role": "user", "content": mesaj})

                    yanit = self._beyin.uret(sistem, msg_list)
                    sonuc["cevap"] = yanit.strip() if yanit else "Anlayamadim."
                except Exception as e:
                    sonuc["cevap"] = "Bir hata olustu: " + str(e)[:60]

            t = threading.Thread(target=_cagir, daemon=True)
            t.start()
            t.join(timeout=30)

            if sonuc["cevap"] is None:
                logger.warning("[%s] Beyin 30sn timeout!", self.bot_ad)
                sonuc["cevap"] = "Uzgunum, yanit uretilemedi. (timeout)"
            else:
                if ONCE_HAFIZA_KAYDET is not None:
                    try:
                        ONCE_HAFIZA_KAYDET(
                            mesaj, "discord_sohbet", sonuc["cevap"], basari=True
                        )
                    except Exception as e:
                        log.warning(f"[discord_bot] Hafiza kaydi hatasi: {e}")
                        pass
                if session_id:
                    self.konusma_ekle(session_id, mesaj, sonuc["cevap"])

            return sonuc["cevap"][:2000]

        return "AI modulu aktif degil."

    # ── Komut isleyici ────────────────────────────────────────────────

    def komut_isle(self, channel, author, text: str) -> bool:
        """Discord slash komutlarini isle.

        Desteklenen komutlar:
          /new, /stop, /retry, /model, /status
        """
        if not text.startswith(COMMAND_PREFIX):
            return False

        parts = text.strip().split(None, 1)
        komut = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        session_id = str(channel.id)

        async def _send(msg: str):
            try:
                await channel.send(msg[:2000])
            except Exception as e:
                logger.error("[%s] Mesaj gonderilemedi: %s", self.bot_ad, e)

        # — /new — Yeni session baslat
        if komut == COMMAND_PREFIX + "new":
            self.session_sifirla(session_id)
            asyncio.create_task(
                _send("✅ Yeni konusma baslatildi! Nasil yardimci olabilirim?")
            )
            return True

        # — /stop — Aktif gorevi durdur
        elif komut == COMMAND_PREFIX + "stop":
            gorev = self._gorevler.pop(session_id, None)
            if gorev:
                asyncio.create_task(_send("⏹️ Gorev durduruldu."))
            else:
                asyncio.create_task(_send("Aktif gorev yok."))
            return True

        # — /retry — Son yaniti yeniden dene
        elif komut == COMMAND_PREFIX + "retry":
            gecmis = self.session_gecmisi_al(session_id)
            if gecmis:
                son_mesaj = gecmis[-1].get("kullanici", "")
                if son_mesaj:
                    # Son kullanici mesajini yeniden isle
                    cevap = self.ai_yanit_uret(son_mesaj, session_id=session_id)
                    # Channel'a gonder
                    asyncio.create_task(channel.send(cevap[:2000]))
                    return True
            asyncio.create_task(_send("Yenilenecek mesaj bulunamadi."))
            return True

        # — /model — Model goster
        elif komut == COMMAND_PREFIX + "model":
            if not arg:
                asyncio.create_task(
                    _send(f"🤖 Model: {self.ayarlar.get('model')} (kilitli)")
                )
            else:
                asyncio.create_task(
                    _send(
                        "❌ Model degistirme devre disi. Sadece deepseek-v4-flash kullanilir."
                    )
                )
            return True

        # — /status — Bot durumu
        elif komut == COMMAND_PREFIX + "status":
            satirlar = [
                f"🤖 **{self.bot_ad}**",
                f"Model: {self.ayarlar.get('model')}",
                f"Provider: {self.ayarlar.get('provider')}",
                f"Bilinen kanal: {len(self.ayarlar.get('bilinen_kanallar', []))}",
                f"Session gecmisi: {len(self.session_gecmisi_al(session_id))} mesaj",
                f"Aktif gorev: {'✅' if session_id in self._gorevler else '❌'}",
            ]
            asyncio.create_task(channel.send("\n".join(satirlar)))
            return True

        # — /help — Yardim
        elif komut == COMMAND_PREFIX + "help":
            yardim = (
                f"**ReYMeN Discord Bot**\n\n"
                f"{COMMAND_PREFIX}new     — Yeni konusma baslat\n"
                f"{COMMAND_PREFIX}stop    — Aktif gorevi durdur\n"
                f"{COMMAND_PREFIX}retry   — Son yaniti yeniden dene\n"
                f"{COMMAND_PREFIX}model   — Model bilgisi goster\n"
                f"{COMMAND_PREFIX}status  — Bot durumu\n"
                f"{COMMAND_PREFIX}help    — Bu liste\n\n"
                f"Herhangi bir mesaj yazarak AI ile konusabilirsiniz."
            )
            asyncio.create_task(channel.send(yardim))
            return True

        # — Ortak komut modulune yonlendir —
        if ortak_komut_isle is not None:
            try:
                # Ortak komutlar icin async wrapper
                def _gonder_async(cid, metin):
                    asyncio.create_task(channel.send(metin[:2000]))

                return ortak_komut_isle(text, _gonder_async, channel.id)
            except Exception as e:
                log.warning(f"[discord_bot] Mesaj gonderme hatasi: {e}")
                pass

        return False

    # ── Mesaj isleyici (on_message event) ──────────────────────────────

    async def on_message(self, message):
        """Discord on_message event handler.

        Args:
            message: discord.Message nesnesi
        """
        if message.author.bot:
            return  # Kendi mesajlarini ignore et

        channel = message.channel
        session_id = str(channel.id)

        # Kanal kaydet
        self.kanal_ekle(channel.id)

        text = message.content.strip()
        if not text:
            return

        logger.info(
            "[%s] [%s] %s: %.60s", self.bot_ad, channel.id, message.author, text
        )

        # Komut kontrol
        if self.komut_isle(channel, message.author, text):
            return

        # AI yaniti uret (arka planda DM veya kanalda)
        async with channel.typing():
            cevap = await asyncio.get_event_loop().run_in_executor(
                None, self.ai_yanit_uret, text, session_id
            )

        try:
            await channel.send(cevap[:2000])
        except Exception as e:
            logger.error("[%s] Mesaj gonderilemedi: %s", self.bot_ad, e)

    # ── Bot baslatma ──────────────────────────────────────────────────

    async def _on_ready(self):
        """Bot hazir oldugunda tetiklenir."""
        logger.info("[%s] ✅ Discord bot hazir! (%s)", self.bot_ad, self._bot.user)
        self.bot_ad = str(self._bot.user)

        # durum.json'u guncelle (gercek adla)
        _durum_guncelle(self.bot_ad)

        # Bilinen kanallara startup mesaji gonder
        for kanal_id in self.ayarlar.get("bilinen_kanallar", []):
            try:
                kanal = self._bot.get_channel(kanal_id)
                if kanal:
                    await kanal.send(f"🟢 {self.bot_ad} Gateway Ready!")
            except Exception as e:
                logger.warning(
                    "[%s] Startup mesaji gonderilemedi [%s]: %s",
                    self.bot_ad,
                    kanal_id,
                    e,
                )

    def run(self):
        """Discord bot'u baslat ve calistir."""
        if not DISCORD_AVAILABLE:
            logger.error("discord.py (py-cord) kurulu degil! pip install discord.py")
            return

        if not TOKEN:
            logger.error("DISCORD_BOT_TOKEN ayarli degil! .env dosyasini kontrol edin.")
            return

        intents = discord.Intents.default()
        intents.message_content = True  # Mesaj icerigini okumak icin gerekli

        self._bot = commands.Bot(
            command_prefix=COMMAND_PREFIX,
            intents=intents,
            help_command=None,  # Kendi help komutumuz var
        )

        @self._bot.event
        async def on_ready():
            await self._on_ready()

        @self._bot.event
        async def on_message(message):
            await self.on_message(message)

        logger.info("[%s] Discord bot baslatiliyor...", self.bot_ad)
        self._bot.run(TOKEN, log_handler=None)


# ============================================================================
# GATEWAY / MOTOR ENTEGRASYON
# ============================================================================


def motor_kaydet(motor):
    """Motor'a DISCORD_GONDER aracini ekle."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "DISCORD_GONDER",
        lambda metin="", kanal_id="": (
            f"[Discord] HEDEF: {kanal_id}, MESAJ: {metin[:100]}"
            if metin
            else "[Discord] Gonderim aracı kayitli (arkaplan bot ile)."
        ),
        "Discord kanalina mesaj gonder (metin, kanal_id gerekli)",
    )
    motor._plugin_arac_kaydet(
        "DISCORD_BOT_GONDER",
        lambda metin="", kanal_id="": (
            f"[Discord] HEDEF: {kanal_id}, MESAJ: {metin[:100]}"
            if metin
            else "[Discord] Gonderim aracı kayitli."
        ),
        "Discord bot ile mesaj gonder (metin, kanal_id gerekli)",
    )


# ============================================================================
# ANA GIRIS
# ============================================================================


def main():
    """Ana giris noktasi.

    Discord bot'unu baslatir.
    """
    if not DISCORD_AVAILABLE:
        logger.error("discord.py kurulu degil! pip install discord.py")
        sys.exit(1)

    if not TOKEN:
        logger.error("DISCORD_BOT_TOKEN ayarli degil! .env dosyasini kontrol edin.")
        sys.exit(1)

    logger.info("Discord bot baslatiliyor...")
    bot = DiscordBotProcess(TOKEN)
    bot.run()


if __name__ == "__main__":
    main()
