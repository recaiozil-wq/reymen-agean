# -*- coding: utf-8 -*-
"""
telegram_bot/ai_bot.py — ReYMeN AI Agent Bot (Hermes gateway bagimsiz).

Her bot ayri bir BotProcess instance'i olarak calisir.
Beyin + OnceHafiza + ConversationLoop (opsiyonel) ile AI yanit uretir.

Kullanim:
    BOT_TOKEN=xxx BOT_AD=@botad python telegram_bot/ai_bot.py

Kompakt (run_reymen_bots.py uzerinden):
    python run_reymen_bots.py
"""

import json
import logging
import os
import re
import sys
import threading
import time
from pathlib import Path

import requests

# ── Proje kokunu sys.path'e ekle ──────────────────────────────────────────
_PROJE_KOK = Path(__file__).parent.parent.resolve()
if str(_PROJE_KOK) not in sys.path:
    sys.path.insert(0, str(_PROJE_KOK))

# ── Logger ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(message)s",
)
log = logging.getLogger("ai_bot")

# ── Import ReYMeN modulleri (graceful degrade) ────────────────────────────
BEYIN = None
ONCE_HAFIZA_ARA = None
ONCE_HAFIZA_KAYDET = None
CONVERSATION_LOOP = None

try:
    from reymen.cereyan.beyin import Beyin as _B
    BEYIN = _B
except ImportError as e:
    log.warning("Beyin import edilemedi: %s", e)

try:
    from reymen.cereyan.once_hafiza import hafizada_ara as _ara, kaydet as _kaydet
    ONCE_HAFIZA_ARA = _ara
    ONCE_HAFIZA_KAYDET = _kaydet
except ImportError as e:
    log.warning("OnceHafiza import edilemedi: %s", e)

try:
    from reymen.cereyan.conversation_loop import ConversationLoop as _CL
    CONVERSATION_LOOP = _CL
except ImportError as e:
    log.warning("ConversationLoop import edilemedi: %s", e)

# ── Varsayilan ayarlar ────────────────────────────────────────────────────
_VARSAYILAN_AYARLAR = {
    "offset": 0,
    "model": "deepseek-v4-flash",
    "provider": "deepseek",
    "sistem_prompt": (
        "Sen ReYMeN adinda yardimsever bir AI asistanisin. "
        "Kisa ve oz cevap ver. Turkce konus. Sohbet et, sorulari yanitla."
    ),
    "bilinen_chatler": [],
    "konusma_gecmisi": [],  # son 10 mesaj
}


# ═══════════════════════════════════════════════════════════════════════════
# BotProcess — Her bot icin AI Agent Orchestrator
# ═══════════════════════════════════════════════════════════════════════════
class BotProcess:
    """Tek bir Telegram botu icin AI Agent Orchestrator.

    - Beyin ile LLM yaniti uretir
    - OnceHafiza ile hafiza kontrolu yapar (guven > 0.7 ise direkt don)
    - Konusma gecmisi tutar (son 10 mesaj)
    - Telegram polling dongusu ile mesaj dinler
    """

    def __init__(self, token: str, bot_ad: str = ""):
        self.token = token
        self.bot_ad = bot_ad or self._bot_bilgisi_al()
        self.ayar_dosyasi = _PROJE_KOK / ".ReYMeN" / f"ai_bot_{self.bot_ad.replace('@','')}.json"
        self.ayarlar: dict = dict(_VARSAYILAN_AYARLAR)
        self._beyin = None
        self._loop = None
        self._ayar_yukle()
        self._beyin_baslat()
        log.info("[%s] BotProcess baslatildi", self.bot_ad)

    # ── Bot bilgisi ────────────────────────────────────────────────────
    def _bot_bilgisi_al(self) -> str:
        try:
            r = requests.get(
                f"https://api.telegram.org/bot{self.token}/getMe", timeout=5
            )
            return f"@{r.json()['result']['username']}"
        except Exception:
            return "@?"

    # ── Ayar yonetimi ──────────────────────────────────────────────────
    def _ayar_yukle(self):
        try:
            if self.ayar_dosyasi.exists():
                okunan = json.loads(self.ayar_dosyasi.read_text(encoding="utf-8"))
                self.ayarlar.update(okunan)
        except Exception as e:
            log.warning("[%s] Ayar yukleme hatasi: %s", self.bot_ad, e)

    def _ayar_kaydet(self):
        try:
            self.ayar_dosyasi.parent.mkdir(parents=True, exist_ok=True)
            self.ayar_dosyasi.write_text(
                json.dumps(self.ayarlar, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            log.error("[%s] Ayar kaydedilemedi: %s", self.bot_ad, e)

    def offset_guncelle(self, yeni_offset: int):
        if yeni_offset > self.ayarlar.get("offset", 0):
            self.ayarlar["offset"] = yeni_offset
            self._ayar_kaydet()

    def chat_ekle(self, chat_id: int):
        chatler = self.ayarlar.setdefault("bilinen_chatler", [])
        if chat_id not in chatler:
            chatler.append(chat_id)
            self.ayarlar["bilinen_chatler"] = chatler
            self._ayar_kaydet()

    def konusma_ekle(self, kullanici: str, asistan: str, maks: int = 10):
        gecmis = self.ayarlar.setdefault("konusma_gecmisi", [])
        gecmis.append({"kullanici": kullanici, "asistan": asistan})
        if len(gecmis) > maks:
            self.ayarlar["konusma_gecmisi"] = gecmis[-maks:]
        self._ayar_kaydet()

    # ── Beyin baslat ──────────────────────────────────────────────────
    def _beyin_baslat(self):
        """Beyin + ConversationLoop baslat."""
        if BEYIN is None:
            log.warning("[%s] Beyin modulu yuklu degil!", self.bot_ad)
            return

        provider = self.ayarlar.get("provider", "deepseek")
        model = self.ayarlar.get("model", "deepseek-v4-flash")

        # .env'den API key al
        deepseek_key = os.environ.get("DEEPSEEK_API_KEY", "")
        openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")

        cfg = {
            "default_provider": provider,
            "default_model": model,
            "providers": {
                "deepseek": {
                    "base_url": "https://api.deepseek.com",
                    "api_key": deepseek_key or os.environ.get("DEEPSEEK_API_KEY", ""),
                },
                "openrouter": {
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": openrouter_key or os.environ.get("OPENROUTER_API_KEY", ""),
                },
            },
        }
        try:
            self._beyin = BEYIN(cfg)
        except Exception as e:
            log.error("[%s] Beyin baslatma hatasi: %s", self.bot_ad, e)
            return

        # ConversationLoop (opsiyonel — tool kullanimi icin)
        if CONVERSATION_LOOP is not None:
            try:
                self._loop = CONVERSATION_LOOP(beyin=self._beyin, motor=None, max_tur=5)
            except Exception as e:
                log.warning("[%s] ConversationLoop baslatma hatasi: %s", self.bot_ad, e)

        log.info("[%s] Beyin aktif: %s / %s", self.bot_ad, provider, model)

    # ── AI yanit uret ──────────────────────────────────────────────────
    def ai_yanit_uret(self, mesaj: str) -> str:
        """OnceHafiza + Beyin ile yanit uret (30sn timeout)."""
        import threading as _thr

        # 1. OnceHafiza kontrolu
        if ONCE_HAFIZA_ARA is not None:
            try:
                h = ONCE_HAFIZA_ARA(mesaj, kategori="")
                if h and len(h) > 0:
                    kayit = h[0] if isinstance(h[0], dict) else {}
                    guven = kayit.get("guven", 0) if isinstance(kayit, dict) else 0
                    if guven > 0.7:
                        cozum = kayit.get("cozum", "") if isinstance(kayit, dict) else (kayit[3] if len(kayit) > 3 else "")
                        if cozum:
                            return cozum[:2000]
            except Exception:
                pass

        # 2. Dogrudan Beyin (30sn timeout ile)
        if self._beyin is not None:
            sonuc = {"cevap": None}

            def _cagir():
                try:
                    sistem = self.ayarlar.get("sistem_prompt", _VARSAYILAN_AYARLAR["sistem_prompt"])
                    gecmis = self.ayarlar.get("konusma_gecmisi", [])
                    msg_list = []
                    for kayit in gecmis[-5:]:
                        if isinstance(kayit, dict):
                            if kayit.get("kullanici"):
                                msg_list.append({"role": "user", "content": kayit["kullanici"]})
                            if kayit.get("asistan"):
                                msg_list.append({"role": "assistant", "content": kayit["asistan"]})
                    msg_list.append({"role": "user", "content": mesaj})
                    yanit = self._beyin.uret(sistem, msg_list)
                    sonuc["cevap"] = yanit.strip() if yanit else "Anlayamadim."
                except Exception as e:
                    sonuc["cevap"] = "Bir hata olustu: " + str(e)[:60]

            t = _thr.Thread(target=_cagir, daemon=True)
            t.start()
            t.join(timeout=30)

            if sonuc["cevap"] is None:
                log.warning("[%s] Beyin 30sn timeout!", self.bot_ad)
                sonuc["cevap"] = "Uzgunum, yanit uretilemedi. (timeout)"
            else:
                if ONCE_HAFIZA_KAYDET is not None:
                    try:
                        ONCE_HAFIZA_KAYDET(mesaj, "bot_sohbet", sonuc["cevap"], basari=True)
                    except Exception:
                        pass
                self.konusma_ekle(mesaj, sonuc["cevap"])

            return sonuc["cevap"][:2000]

        return "AI modulu aktif degil."

    # ── Telegram mesaj gonder ─────────────────────────────────────────
    def mesaj_gonder(self, chat_id: int, metin: str) -> bool:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{self.token}/sendMessage",
                json={"chat_id": chat_id, "text": metin[:4096]},
                timeout=10,
            )
            return r.ok
        except Exception as e:
            log.error("[%s] Mesaj gonderilemedi: %s", self.bot_ad, e)
            return False

    def mesaj_sil(self, chat_id: int, msg_id: int):
        try:
            requests.post(
                f"https://api.telegram.org/bot{self.token}/deleteMessage",
                json={"chat_id": chat_id, "message_id": msg_id},
                timeout=5,
            )
        except Exception:
            pass

    # ── Komut isleyici ────────────────────────────────────────────────
    def komut_isle(self, chat_id: int, text: str) -> bool:
        """Slash komutlarini isle. True=komuttu, False=normal mesaj."""
        if not text.startswith("/"):
            return False

        parts = text.strip().split(None, 1)
        komut = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if komut == "/start":
            self.mesaj_gonder(chat_id, f"Merhaba! Ben {self.bot_ad} AI asistaniyim.")
        elif komut == "/model":
            if not arg:
                self.mesaj_gonder(chat_id, f"Model: {self.ayarlar.get('model')}")
            else:
                self.ayarlar["model"] = arg
                self._ayar_kaydet()
                self._beyin_baslat()
                self.mesaj_gonder(chat_id, f"Model guncellendi: {arg}")
        elif komut == "/provider":
            if not arg:
                self.mesaj_gonder(chat_id, f"Provider: {self.ayarlar.get('provider')}")
            else:
                self.ayarlar["provider"] = arg
                self._ayar_kaydet()
                self._beyin_baslat()
                self.mesaj_gonder(chat_id, f"Provider guncellendi: {arg}")
        elif komut == "/sistem":
            if not arg:
                self.mesaj_gonder(chat_id, f"Sistem prompt:\n{self.ayarlar.get('sistem_prompt','')[:200]}")
            else:
                self.ayarlar["sistem_prompt"] = arg
                self._ayar_kaydet()
                self.mesaj_gonder(chat_id, "Sistem prompt guncellendi.")
        elif komut == "/ayarlar":
            o = self.ayarlar
            self.mesaj_gonder(chat_id,
                f"Model: {o.get('model')}\n"
                f"Provider: {o.get('provider')}\n"
                f"Chatler: {len(o.get('bilinen_chatler', []))}\n"
                f"Konusma: {len(o.get('konusma_gecmisi', []))} mesaj"
            )
        elif komut == "/sifirla":
            offset = self.ayarlar.get("offset", 0)
            self.ayarlar = dict(_VARSAYILAN_AYARLAR)
            self.ayarlar["offset"] = offset
            self._ayar_kaydet()
            self._beyin_baslat()
            self.mesaj_gonder(chat_id, "Ayarlar sifirlandi.")
        else:
            return False
        return True

    # ── Polling dongusu ──────────────────────────────────────────────
    def poll(self, durma_events=None):
        """Ana polling dongusu. Sonsuz calisir."""
        if durma_events is None:
            durma_events = []

        # Webhook temizle
        try:
            requests.get(
                f"https://api.telegram.org/bot{self.token}/deleteWebhook?drop_pending_updates=true",
                timeout=5,
            )
        except Exception:
            pass

        offset = self.ayarlar.get("offset", 0)
        log.info("[%s] Polling basliyor, offset=%s", self.bot_ad, offset)

        # Startup bildirimi
        for cid in self.ayarlar.get("bilinen_chatler", []):
            self.mesaj_gonder(cid, f"{self.bot_ad} Gateway Starting")

        while True:
            # Durma kontrolu
            for evt in durma_events:
                if evt and evt.is_set():
                    log.info("[%s] Durma istegi alindi.", self.bot_ad)
                    return

            try:
                r = requests.post(
                    f"https://api.telegram.org/bot{self.token}/getUpdates",
                    json={"offset": offset, "timeout": 30, "allowed_updates": ["message"]},
                    timeout=35,
                )
                data = r.json()
                if not data.get("ok"):
                    if "409" in str(data):
                        log.warning("[%s] 409 Conflict — 10sn bekleniyor...", self.bot_ad)
                        time.sleep(10)
                        continue
                    log.warning("[%s] API hatasi: %s", self.bot_ad, data)
                    time.sleep(3)
                    continue

                for update in data.get("result", []):
                    yeni_offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    text = msg.get("text", "")
                    chat_id = msg.get("chat", {}).get("id", 0)
                    from_user = msg.get("from", {}).get("first_name", "?")

                    offset = yeni_offset
                    self.offset_guncelle(yeni_offset)

                    if chat_id:
                        self.chat_ekle(chat_id)
                    if not text:
                        continue

                    log.info("[%s] [%s] %s: %.60s", self.bot_ad, chat_id, from_user, text)

                    # Komut mu?
                    if self.komut_isle(chat_id, text):
                        continue

                    # AI yaniti (bekleme mesaji gonderilmez)
                    # bekle = self.mesaj_gonder(chat_id, "Dusunuyorum...")
                    cevap = self.ai_yanit_uret(text)
                    self.mesaj_gonder(chat_id, cevap)

            except requests.exceptions.Timeout:
                continue
            except Exception as e:
                log.error("[%s] Dongu hatasi: %s", self.bot_ad, e)
                time.sleep(3)
                continue


# ═══════════════════════════════════════════════════════════════════════════
# Ana giris — tek bot
# ═══════════════════════════════════════════════════════════════════════════
def main():
    token = os.environ.get("BOT_TOKEN", "") or os.environ.get("TELEGRAM_BOT_TOKEN", "")
    bot_ad = os.environ.get("BOT_AD", "")

    # .env dosyalarini yukle (API anahtarlari icin)
    _env_yukle = lambda p: os.path.exists(p) and __import__('dotenv').load_dotenv(p, override=True)
    _env_yukle(os.path.join(os.path.dirname(__file__), "..", "reymen", "sistem", ".env"))
    _env_yukle(os.path.join(os.path.dirname(__file__), "..", ".env"))

    if not token or token.startswith("***"):
        log.error("BOT_TOKEN bulunamadi! BOT_TOKEN env var veya TELEGRAM_BOT_TOKEN gerekli.")
        sys.exit(1)

    bot = BotProcess(token, bot_ad)
    log.info("Bot baslatildi: %s", bot.bot_ad)
    bot.poll()


if __name__ == "__main__":
    main()
