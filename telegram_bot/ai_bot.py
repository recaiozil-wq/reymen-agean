"""
telegram_bot/ai_bot.py — ReYMeN AI-powered Telegram Bot.
Basit polling dongusu, 409 hatasinda otomatik yeniden baglanir.
@Kiral38bot ile AI sohbet yapar.

Kalıcı ayarlar: .ReYMeN/ai_bot_ayarlari.json
  - offset: son okunan Telegram update_id (restart'ta tekrar okumasın)
  - model, provider, sistem_prompt: runtime'da /model /provider /sistem ile değiştirilebilir
  - bilinen_chatler: startup bildirimi gönderilecek chat ID'leri

Komutlar:
  /start              — Hoş geldin mesajı
  /model <model>      — Model değiştir (deepseek-chat, gpt-4o-mini ...)
  /provider <prov>    — Provider değiştir (deepseek, openrouter ...)
  /sistem <prompt>    — Sistem promptunu değiştir
  /ayarlar            — Mevcut ayarları göster
  /sifirla            — Ayarları varsayılana döndür

Kullanim: python telegram_bot/ai_bot.py
"""
import json
import logging
import os
import sys
import time
from pathlib import Path

import requests
import logging
logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
log = logging.getLogger("ai_bot")

PROJE_KOK = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJE_KOK))

# Kalıcı ayar dosyası
AYAR_DOSYASI = PROJE_KOK / ".ReYMeN" / "ai_bot_ayarlari.json"

# Varsayılan ayarlar
VARSAYILAN_AYARLAR = {
    "offset": 0,
    "model": "deepseek-chat",
    "provider": "deepseek",
    "sistem_prompt": (
        "Sen ReYMeN adinda yardimsever bir AI asistanisin. "
        "Kisa ve oz cevap ver. Turkce konus. Sohbet et, sorulari yanitla."
    ),
    "bilinen_chatler": [],
}


# ── Kalıcı Ayar Yöneticisi ───────────────────────────────────────────────────

class AyarYoneticisi:
    """JSON dosyasına kalıcı ayarları oku/yaz."""

    def __init__(self, dosya: Path):
        self._dosya = dosya
        self._ayarlar = dict(VARSAYILAN_AYARLAR)
        self._yukle()

    def _yukle(self):
        """Dosyadan ayarları yükle (yoksa varsayılan kullan)."""
        try:
            if self._dosya.exists():
                okunan = json.loads(self._dosya.read_text(encoding="utf-8"))
                self._ayarlar.update(okunan)
        except Exception as e:
            log.warning(f"Ayar dosyası okunamadı, varsayılan kullanılıyor: {e}")

    def _kaydet(self):
        """Ayarları dosyaya yaz."""
        try:
            self._dosya.parent.mkdir(parents=True, exist_ok=True)
            self._dosya.write_text(
                json.dumps(self._ayarlar, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            log.error(f"Ayar kaydedilemedi: {e}")

    def al(self, anahtar, varsayilan=None):
        return self._ayarlar.get(anahtar, varsayilan)

    def ayarla(self, anahtar, deger):
        self._ayarlar[anahtar] = deger
        self._kaydet()

    def offset_guncelle(self, yeni_offset: int):
        """Offset'i güncelle ve kaydet."""
        if yeni_offset > self._ayarlar.get("offset", 0):
            self._ayarlar["offset"] = yeni_offset
            self._kaydet()

    def chat_ekle(self, chat_id: int):
        """Bilinen chatler listesine chat_id ekle."""
        chatler = self._ayarlar.get("bilinen_chatler", [])
        if chat_id not in chatler:
            chatler.append(chat_id)
            self._ayarlar["bilinen_chatler"] = chatler
            self._kaydet()

    def sifirla(self):
        """Offset hariç tüm ayarları varsayılana döndür."""
        offset = self._ayarlar.get("offset", 0)
        self._ayarlar = dict(VARSAYILAN_AYARLAR)
        self._ayarlar["offset"] = offset
        self._kaydet()

    def ozet(self) -> str:
        return (
            f"Model: {self._ayarlar.get('model')}\n"
            f"Provider: {self._ayarlar.get('provider')}\n"
            f"Sistem: {self._ayarlar.get('sistem_prompt', '')[:80]}...\n"
            f"Offset: {self._ayarlar.get('offset')}\n"
            f"Bilinen chatler: {self._ayarlar.get('bilinen_chatler')}"
        )


# ── Token ────────────────────────────────────────────────────────────────────

def token_al():
    """TELEGRAM_BOT_TOKEN al (önce .env, sonra env var)."""
    env_file = PROJE_KOK / ".env"
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token or token.startswith("***"):
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    val = line.split("=", 1)[1].strip()
                    if val and not val.startswith("***"):
                        token = val
                        break
    return token


# ── AI Yanıt ─────────────────────────────────────────────────────────────────

def ai_yanit_uret(mesaj: str, ayarlar: AyarYoneticisi) -> str:
    """ReYMeN AI motoru ile yanıt üret (kalıcı ayarları kullanarak). OnceHafiza'ya bakar, varsa direkt dondur."""
    # ── OnceHafiza kontrolu ──────────────────────────────────────
    try:
        if str(PROJE_KOK) not in sys.path:
            sys.path.insert(0, str(PROJE_KOK))
        from reymen.cereyan.once_hafiza import hafizada_ara, kaydet
        _h = hafizada_ara(mesaj, kategori="")
        if _h and _h[0].get("guven", 0) > 0.7:
            _c = _h[0].get("cozum", "")
            if _c:
                return _c[:2000]
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")

    try:
        from dotenv import load_dotenv
        load_dotenv(str(PROJE_KOK / ".env"))

        from beyin import Beyin
        provider = ayarlar.al("provider", "deepseek")
        model = ayarlar.al("model", "deepseek-chat")
        cfg = {
            "default_provider": provider,
            "default_model": model,
            "providers": {
                "deepseek": {
                    "base_url": "https://api.deepseek.com",
                    "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
                },
                "openrouter": {
                    "base_url": "https://openrouter.ai/api/v1",
                    "api_key": os.environ.get("OPENROUTER_API_KEY", ""),
                },
            },
        }
        beyin = Beyin(cfg)
        sistem = ayarlar.al("sistem_prompt", VARSAYILAN_AYARLAR["sistem_prompt"])
        yanit = beyin.uret(sistem, [{"role": "user", "content": mesaj}])
        _cevap = yanit.strip() if yanit else "Anlayamadim."
        # Cevabi hafizaya kaydet
        try:
            from reymen.cereyan.once_hafiza import kaydet as _kaydet
            _kaydet(mesaj, "bot_sohbet", _cevap, basari=True)
        except Exception:
            logger.warning("[fix_01_sessiz_except] Exception")
        return _cevap
    except Exception as e:
        log.error(f"AI hatasi: {e}")
        return f"Bir hata olustu: {str(e)[:80]}"


# ── Telegram Gönderici ────────────────────────────────────────────────────────

def mesaj_gonder(token: str, chat_id: int, metin: str) -> bool:
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": metin[:4096]},
            timeout=10,
        )
        return r.ok
    except Exception as e:
        log.error(f"Mesaj gönderilemedi: {e}")
        return False


def mesaj_sil(token: str, chat_id: int, msg_id: int):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/deleteMessage",
            json={"chat_id": chat_id, "message_id": msg_id},
            timeout=5,
        )
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")


# ── Komut İşleyici ────────────────────────────────────────────────────────────

def komut_isle(token: str, chat_id: int, text: str, ayarlar: AyarYoneticisi) -> bool:
    """Slash komutunu işle. True → komuttu, False → normal mesaj."""
    if not text.startswith("/"):
        return False

    parcalar = text.strip().split(None, 1)
    komut = parcalar[0].lower()
    arguman = parcalar[1].strip() if len(parcalar) > 1 else ""

    if komut == "/start":
        mesaj_gonder(token, chat_id, "Merhaba! Ben ReYMeN AI asistaniyim. Nasil yardimci olabilirim?")

    elif komut == "/model":
        if not arguman:
            mesaj_gonder(token, chat_id, f"Mevcut model: {ayarlar.al('model')}\nKullanim: /model deepseek-chat")
        else:
            ayarlar.ayarla("model", arguman)
            mesaj_gonder(token, chat_id, f"Model guncellendi: {arguman}")
            log.info(f"Model degistirildi: {arguman}")

    elif komut == "/provider":
        if not arguman:
            mesaj_gonder(token, chat_id, f"Mevcut provider: {ayarlar.al('provider')}\nKullanim: /provider deepseek")
        else:
            ayarlar.ayarla("provider", arguman)
            mesaj_gonder(token, chat_id, f"Provider guncellendi: {arguman}")
            log.info(f"Provider degistirildi: {arguman}")

    elif komut == "/sistem":
        if not arguman:
            mesaj_gonder(token, chat_id, f"Mevcut sistem prompt:\n{ayarlar.al('sistem_prompt')}")
        else:
            ayarlar.ayarla("sistem_prompt", arguman)
            mesaj_gonder(token, chat_id, f"Sistem prompt guncellendi.")
            log.info("Sistem prompt degistirildi.")

    elif komut == "/ayarlar":
        mesaj_gonder(token, chat_id, f"Mevcut ayarlar:\n{ayarlar.ozet()}")

    elif komut == "/sifirla":
        ayarlar.sifirla()
        mesaj_gonder(token, chat_id, "Ayarlar varsayilana donduruld. Model ve provider sifirlandi.")
        log.info("Ayarlar sifirlandi.")

    else:
        return False  # Bilinmeyen komut → normal mesaj olarak işle

    return True


# ── Ana Döngü ─────────────────────────────────────────────────────────────────

def main():
    token = token_al()
    if not token:
        log.error("TELEGRAM_BOT_TOKEN bulunamadi!")
        sys.exit(1)

    ayarlar = AyarYoneticisi(AYAR_DOSYASI)
    log.info(f"Ayarlar yuklendi: model={ayarlar.al('model')}, provider={ayarlar.al('provider')}")

    # Bot bilgisi al
    bot_adi = ""
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
        bot_adi = r.json()["result"]["username"]
        log.info(f"Baglanildi: @{bot_adi}")
    except Exception as e:
        log.error(f"Baglanti hatasi: {e}")
        sys.exit(1)

    # Webhook'u temizle
    requests.get(
        f"https://api.telegram.org/bot{token}/deleteWebhook?drop_pending_updates=true",
        timeout=5,
    )

    # Startup bildirimi — bilinen chatlere "Gateway Starting" gönder
    for chat_id in ayarlar.al("bilinen_chatler", []):
        mesaj_gonder(token, chat_id, f"@{bot_adi} Gateway Starting\nModel: {ayarlar.al('model')} | Provider: {ayarlar.al('provider')}")
        log.info(f"Startup bildirimi gonderildi: {chat_id}")

    # Kalıcı offset'i yükle
    offset = ayarlar.al("offset", 0)
    log.info(f"Polling basliyor, offset={offset}")

    while True:
        try:
            r = requests.post(
                f"https://api.telegram.org/bot{token}/getUpdates",
                json={"offset": offset, "timeout": 30, "allowed_updates": ["message"]},
                timeout=35,
            )
            data = r.json()
            if not data.get("ok"):
                if "409" in str(data):
                    log.warning("409 Conflict — 5sn bekleyip tekrar...")
                    time.sleep(5)
                    continue
                log.warning(f"API hatasi: {data}")
                time.sleep(3)
                continue

            for update in data.get("result", []):
                yeni_offset = update["update_id"] + 1
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat_id = msg.get("chat", {}).get("id", 0)
                from_user = msg.get("from", {}).get("first_name", "?")

                # Kalıcı offset güncelle (her update sonrası)
                offset = yeni_offset
                ayarlar.offset_guncelle(yeni_offset)

                # Chat'i bilinen listesine ekle
                if chat_id:
                    ayarlar.chat_ekle(chat_id)

                if not text:
                    continue

                log.info(f"Mesaj: [{from_user}] {text[:60]}")

                # Slash komut mu?
                if komut_isle(token, chat_id, text, ayarlar):
                    continue

                # AI yanıtı
                bekleme = requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": "Dusunuyorum..."},
                    timeout=5,
                )
                bekleme_msg_id = bekleme.json()["result"]["message_id"] if bekleme.ok else None

                cevap = ai_yanit_uret(text, ayarlar)

                if bekleme_msg_id:
                    mesaj_sil(token, chat_id, bekleme_msg_id)

                mesaj_gonder(token, chat_id, cevap)

        except requests.exceptions.Timeout:
            log.debug("getUpdates timeout (normal)")
            continue
        except Exception as e:
            log.error(f"Hata: {e}")
            time.sleep(3)
            continue


if __name__ == "__main__":
    main()
