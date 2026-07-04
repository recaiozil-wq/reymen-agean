# -*- coding: utf-8 -*-
"""
telegram_bot/ai_bot.py — Kalici ayar yoneticisi ve komut isleyici.

AyarYoneticisi: JSON dosyasina kalici ayarlari oku/yaz.
komut_isle: Slash komutlarini isle.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

log = logging.getLogger("ai_bot")

VARSAYILAN_AYARLAR = {
    "offset": 0,
    "model": "deepseek-chat",
    "provider": "deepseek",
    "sistem_prompt": (
        "Sen ReYMeN adinda yardimsever bir AI asistanisin. "
        "Kisa ve oz cevap ver. Turkce konus."
    ),
    "bilinen_chatler": [],
}


class AyarYoneticisi:
    """JSON dosyasina kalici ayarlari oku/yaz."""

    def __init__(self, dosya: Path):
        self._dosya = Path(dosya)
        self._ayarlar = dict(VARSAYILAN_AYARLAR)
        self._yukle()

    def _yukle(self):
        try:
            if self._dosya.exists():
                okunan = json.loads(self._dosya.read_text(encoding="utf-8"))
                self._ayarlar.update(okunan)
        except Exception as e:
            log.warning(f"Ayar dosyasi okunamadi, varsayilan kullaniliyor: {e}")

    def _kaydet(self):
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
        if yeni_offset > self._ayarlar.get("offset", 0):
            self._ayarlar["offset"] = yeni_offset
            self._kaydet()

    def chat_ekle(self, chat_id: int):
        chatler = self._ayarlar.get("bilinen_chatler", [])
        if chat_id not in chatler:
            chatler.append(chat_id)
            self._ayarlar["bilinen_chatler"] = chatler
            self._kaydet()

    def sifirla(self):
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


def mesaj_gonder(token: str, chat_id: int, metin: str) -> bool:
    return True


def komut_isle(token: str, chat_id: int, text: str, ayarlar: AyarYoneticisi) -> bool:
    if not text.startswith("/"):
        return False

    parcalar = text.strip().split(None, 1)
    komut = parcalar[0].lower()
    arguman = parcalar[1].strip() if len(parcalar) > 1 else ""

    if komut == "/start":
        mesaj_gonder(token, chat_id, "Merhaba! Ben ReYMeN AI asistaniyim.")
    elif komut == "/model":
        if not arguman:
            mesaj_gonder(token, chat_id, f"Mevcut model: {ayarlar.al('model')}")
        else:
            ayarlar.ayarla("model", arguman)
            mesaj_gonder(token, chat_id, f"Model guncellendi: {arguman}")
    elif komut == "/provider":
        if not arguman:
            mesaj_gonder(token, chat_id, f"Mevcut provider: {ayarlar.al('provider')}")
        else:
            ayarlar.ayarla("provider", arguman)
            mesaj_gonder(token, chat_id, f"Provider guncellendi: {arguman}")
    elif komut == "/sistem":
        if not arguman:
            mesaj_gonder(token, chat_id, f"Mevcut sistem prompt:\n{ayarlar.al('sistem_prompt')}")
        else:
            ayarlar.ayarla("sistem_prompt", arguman)
            mesaj_gonder(token, chat_id, "Sistem prompt guncellendi.")
    elif komut == "/ayarlar":
        mesaj_gonder(token, chat_id, f"Mevcut ayarlar:\n{ayarlar.ozet()}")
    elif komut == "/sifirla":
        ayarlar.sifirla()
        mesaj_gonder(token, chat_id, "Ayarlar varsayilana donduruldu.")
    else:
        return False

    return True
