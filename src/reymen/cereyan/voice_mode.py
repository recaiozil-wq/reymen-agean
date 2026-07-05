# -*- coding: utf-8 -*-
"""
voice_mode.py â€” Sesli (Push-to-Talk) arayÃ¼z modÃ¼lÃ¼.

Mikrofondan ses kaydeder, faster-whisper ile metne Ã§evirir,
Beyin (LLM) ile yanÄ±t Ã¼retir, edge-tts ile seslendirir
ve hoparlÃ¶rden oynatÄ±r.

KullanÄ±m:
    from reymen.cereyan.voice_mode import VoiceMode

    vm = VoiceMode(beyin=benim_beyin)
    vm.baslat()         # REPL: dinle / konus / cik
    vm.dinle_ve_cevapla()  # tek seferlik kaydet->STT->LLM->TTS dÃ¶ngÃ¼sÃ¼

BaÄŸÄ±mlÄ±lÄ±klar (opsiyonel â€” eksik olanlar graceful degrade yapar):
    - sounddevice       : mikrofon kaydÄ± + hoparlÃ¶r oynatma
    - numpy             : ses buffer iÅŸlemleri
    - faster-whisper    : yerel STT (CPU/GPU)
    - edge-tts          : Microsoft Edge TTS (Ã¼cretsiz, Ã§evrimiÃ§i)
    - pygame            : alternatif ses oynatÄ±cÄ±
"""

from __future__ import annotations

import io
import json
import logging
import os
import queue
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Generator, Optional

logger = logging.getLogger(__name__)

# â”€â”€ Opsiyonel baÄŸÄ±mlÄ±lÄ±klar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# sounddevice â€” mikrofon kaydÄ± ve hoparlÃ¶r oynatma
try:
    import sounddevice as sd
    import numpy as np

    SD_MEVCUT = True
except ImportError:
    sd = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    SD_MEVCUT = False

# faster-whisper â€” yerel STT motoru
try:
    from faster_whisper import WhisperModel

    _FASTER_WHISPER_MEVCUT = True
except ImportError:
    WhisperModel = None  # type: ignore[assignment]
    _FASTER_WHISPER_MEVCUT = False

# openai â€” Whisper API (alternatif STT)
try:
    from openai import OpenAI

    _OPENAI_MEVCUT = True
except ImportError:
    OpenAI = None  # type: ignore[assignment]
    _OPENAI_MEVCUT = False

# edge-tts â€” Microsoft Edge TTS motoru
try:
    import edge_tts

    _EDGE_TTS_MEVCUT = True
except ImportError:
    edge_tts = None  # type: ignore[assignment]
    _EDGE_TTS_MEVCUT = False

# pygame â€” alternatif ses oynatÄ±cÄ±
try:
    import pygame

    PYGAME_MEVCUT = True
except ImportError:
    pygame = None  # type: ignore[assignment]
    PYGAME_MEVCUT = False

# ffmpeg/ffplay â€” ses oynatma iÃ§in sistem aracÄ±
_FFPLAY_BULUNDU: Optional[str] = None
for _exe in ("ffplay", "ffplay.exe"):
    try:
        _r = subprocess.run(
            ["where" if os.name == "nt" else "which", _exe],
            capture_output=True,
            text=True,
            timeout=3,
        )
        if _r.returncode == 0 and _r.stdout.strip():
            _FFPLAY_BULUNDU = _r.stdout.strip().splitlines()[0]
            break
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")


# â”€â”€ Beyin import (opsiyonel) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _beyin_al() -> Any:
    """Beyin sÄ±nÄ±fÄ±nÄ± dÃ¶ndÃ¼rÃ¼r; yoksa None."""
    try:
        from reymen.cereyan.beyin import Beyin

        return Beyin
    except ImportError:
        return None


# â”€â”€ VarsayÄ±lan sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_VARSAYILAN_SES_KAYNAGI: int = 0  # varsayÄ±lan mikrofon
_VARSAYILAN_ORNEKLEME_HIZI: int = 16000  # Whisper iÃ§in ideal
_VARSAYILAN_KANAL_SAYISI: int = 1  # mono
_VARSAYILAN_KAYIT_SURESI: float = 5.0  # saniye (push-to-talk deÄŸilse)
_VARSAYILAN_DINLEME_ESIÄI: float = 0.02  # ses seviyesi eÅŸiÄŸi (VAD basit)
_VARSAYILAN_SESSIZLIK_SURESI: float = 1.5  # VAD iÃ§in sessizlik timeout
_VARSAYILAN_DIL: str = "tr"  # STT dili
_VARSAYILAN_TTS_SESI: str = "tr-TR-AhmetNeural"  # edge-tts TÃ¼rkÃ§e erkek sesi

# VAD (Voice Activity Detection) parametreleri
_VAD_PENCERE_BOYUTU: int = 1024  # RMS penceresi
_VAD_SESSIZ_EN_COK: int = 15  # kaÃ§ sessiz pencereden sonra dur


# â”€â”€ Ses verisi taÅŸÄ±yÄ±cÄ±sÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class SesKaydi:
    """KaydedilmiÅŸ ses verisini ve Ã¼stverisini taÅŸÄ±r."""

    veri: Optional[Any] = None  # numpy array
    ornekleme_hizi: int = _VARSAYILAN_ORNEKLEME_HIZI
    sure_sn: float = 0.0
    dosya_yolu: Optional[str] = None  # temp wav dosya yolu
    metin: str = ""  # STT Ã§Ä±ktÄ±sÄ±


# â”€â”€ Durum kodlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class VoiceModeDurum:
    """VoiceMode Ã§alÄ±ÅŸma durumlarÄ±."""

    DURDU = "durdu"
    DÄ°NLÄ°YOR = "dinliyor"
    KONUSUYOR = "konusuyor"
    Ä°ÅLÄ°YOR = "isliyor"
    HATA = "hata"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VoiceMode Ana SÄ±nÄ±fÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class VoiceMode:
    """Sesli arayÃ¼z yÃ¶neticisi.

    Push-to-talk ve otomatik VAD ile ses kaydÄ±, STT, LLM yanÄ±tÄ±
    ve TTS Ã§Ä±ktÄ±sÄ±nÄ± tek bir dÃ¶ngÃ¼de birleÅŸtirir.

    Args:
        beyin: Beyin instance'Ä± (LLM baÄŸlantÄ±sÄ±). Yoksa sadece
               kayÄ±t + STT + TTS test edilebilir.
        config: YapÄ±landÄ±rma sÃ¶zlÃ¼ÄŸÃ¼ (opsiyonel).
            Anahtarlar:
                - kaynak_id: mikrofon cihaz indeksi (int)
                - ornekleme_hizi: Ã¶rnekleme hÄ±zÄ± (int)
                - kayit_suresi: maksimum kayÄ±t sÃ¼resi (float)
                - dil: STT dil kodu (str)
                - tts_sesi: edge-tts ses adÄ± (str)
                - stt_backend: "faster_whisper" veya "openai"
                - tts_backend: "edge_tts" (tek seÃ§enek)
                - ses_esiÄŸi: VAD ses eÅŸiÄŸi (float)
                - sessizlik_suresi: VAD timeout (float)
    """

    def __init__(
        self,
        beyin: Optional[Any] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.beyin = beyin
        self._cfg = config or {}

        # â”€â”€ Cihaz yapÄ±landÄ±rmasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.kaynak_id: int = self._cfg.get("kaynak_id", _VARSAYILAN_SES_KAYNAGI)
        self.ornekleme_hizi: int = self._cfg.get(
            "ornekleme_hizi", _VARSAYILAN_ORNEKLEME_HIZI
        )
        self.kanal_sayisi: int = self._cfg.get("kanal_sayisi", _VARSAYILAN_KANAL_SAYISI)
        self.kayit_suresi: float = self._cfg.get(
            "kayit_suresi", _VARSAYILAN_KAYIT_SURESI
        )

        # â”€â”€ STT yapÄ±landÄ±rmasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.dil: str = self._cfg.get("dil", _VARSAYILAN_DIL)
        self.stt_backend: str = self._cfg.get("stt_backend", "faster_whisper")
        self._whisper_model: Optional[Any] = None
        self._openai_client: Optional[Any] = None

        # â”€â”€ TTS yapÄ±landÄ±rmasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.tts_sesi: str = self._cfg.get("tts_sesi", _VARSAYILAN_TTS_SESI)
        self.tts_backend: str = self._cfg.get("tts_backend", "edge_tts")

        # â”€â”€ VAD yapÄ±landÄ±rmasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.ses_esiÄŸi: float = self._cfg.get("ses_esiÄŸi", _VARSAYILAN_DINLEME_ESIÄI)
        self.sessizlik_suresi: float = self._cfg.get(
            "sessizlik_suresi", _VARSAYILAN_SESSIZLIK_SURESI
        )

        # â”€â”€ Ã‡alÄ±ÅŸma durumu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.durum: str = VoiceModeDurum.DURDU
        self._durdurma_olayi = threading.Event()
        self._kilit = threading.Lock()

        # â”€â”€ Ses oynatma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._pygame_ilk = False

        # â”€â”€ Ä°statistik â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.istatistik: dict[str, Any] = {
            "kayit_sayisi": 0,
            "stt_sayisi": 0,
            "tts_sayisi": 0,
            "hata_sayisi": 0,
            "toplam_konusma_suresi": 0.0,
        }

        # BaÅŸlangÄ±Ã§ta kullanÄ±labilirliÄŸi kontrol et
        self._kullanilabilirlik_kontrol()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Kontrol
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _kullanilabilirlik_kontrol(self) -> None:
        """Mevcut baÄŸÄ±mlÄ±lÄ±klarÄ± raporla."""
        eksik: list[str] = []
        if not SD_MEVCUT:
            eksik.append("sounddevice")
        if self.stt_backend == "faster_whisper" and not _FASTER_WHISPER_MEVCUT:
            eksik.append("faster-whisper")
        if self.stt_backend == "openai" and not _OPENAI_MEVCUT:
            eksik.append("openai")
        if not _EDGE_TTS_MEVCUT:
            eksik.append("edge-tts")
        if not PYGAME_MEVCUT and _FFPLAY_BULUNDU is None:
            eksik.append("pygame/ffplay (ses oynatma)")

        if eksik:
            logger.warning(
                "[VoiceMode] Eksik baÄŸÄ±mlÄ±lÄ±klar: %s",
                ", ".join(eksik),
            )

    def kullanilabilir_mi(self) -> dict[str, bool]:
        """KullanÄ±labilirlik durumunu sÃ¶zlÃ¼k olarak dÃ¶ndÃ¼rÃ¼r.

        Returns:
            {
                "mikrofon": bool,
                "hoparlor": bool,
                "stt": bool,
                "tts": bool,
                "beyin": bool,
            }
        """
        return {
            "mikrofon": SD_MEVCUT,
            "hoparlor": SD_MEVCUT or PYGAME_MEVCUT or _FFPLAY_BULUNDU is not None,
            "stt": _FASTER_WHISPER_MEVCUT or _OPENAI_MEVCUT,
            "tts": _EDGE_TTS_MEVCUT,
            "beyin": self.beyin is not None,
        }

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Mikrofon â€” Ses KaydÄ±
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def cihazlari_listele(self) -> list[dict[str, Any]]:
        """KullanÄ±labilir ses cihazlarÄ±nÄ± listeler.

        Returns:
            Her cihaz iÃ§in {'id': int, 'adi': str, 'kanal': int, 'ornek': int}
            listesi. sounddevice yoksa boÅŸ liste.
        """
        if not SD_MEVCUT:
            logger.warning("[VoiceMode] sounddevice yok, cihaz listelenemez.")
            return []
        try:
            cihazlar = []
            for i, c in enumerate(sd.query_devices()):  # type: ignore[arg-type]
                cihazlar.append(
                    {
                        "id": i,
                        "adi": c["name"],
                        "kanal": c["max_input_channels"],
                        "ornek": int(c["default_samplerate"]),
                    }
                )
            return cihazlar
        except Exception as e:
            logger.error("[VoiceMode] Cihaz listeleme hatasÄ±: %s", e)
            return []

    def _vad_ile_kaydet(
        self,
        maks_sure: float = 30.0,
    ) -> Optional[SesKaydi]:
        """Voice Activity Detection ile konuÅŸma algÄ±layarak kaydeder.

        Sessizlik algÄ±landÄ±ÄŸÄ±nda veya maksimum sÃ¼re aÅŸÄ±ldÄ±ÄŸÄ±nda durur.

        Args:
            maks_sure: Maksimum kayÄ±t sÃ¼resi (saniye).

        Returns:
            SesKaydi nesnesi veya baÅŸarÄ±sÄ±zsa None.
        """
        if not SD_MEVCUT:
            logger.error("[VoiceMode] sounddevice gerekli â€” VAD kaydÄ± yapÄ±lamaz.")
            return None

        self.durum = VoiceModeDurum.DÄ°NLÄ°YOR
        print("ğŸ¤ Dinliyor (konuÅŸmayÄ± bÄ±rakÄ±nca otomatik durur)...")

        buffer: list = []
        sessiz_sayac = 0
        baslangic = time.monotonic()

        def _callback(indata: Any, frames: int, _time_info: Any, status: Any) -> None:
            nonlocal sessiz_sayac
            if status:
                logger.debug("[VoiceMode] Ses akÄ±ÅŸÄ± status: %s", status)
            # RMS ses seviyesi
            rms = np.sqrt(np.mean(indata**2))  # type: ignore[operator]
            buffer.append(indata.copy())
            if rms < self.ses_esiÄŸi:
                sessiz_sayac += 1
            else:
                sessiz_sayac = 0

        try:
            with sd.InputStream(
                device=self.kaynak_id,
                samplerate=self.ornekleme_hizi,
                channels=self.kanal_sayisi,
                callback=_callback,
                blocksize=_VAD_PENCERE_BOYUTU,
            ):
                while True:
                    if self._durdurma_olayi.is_set():
                        print("\nâ¹ Durduruldu.")
                        return None
                    if sessiz_sayac > _VAD_SESSIZ_EN_COK:
                        print()  # yeni satÄ±r
                        break
                    if time.monotonic() - baslangic > maks_sure:
                        print("\nâ± Maksimum sÃ¼re aÅŸÄ±ldÄ±.")
                        break
                    time.sleep(0.05)
        except Exception as e:
            logger.error("[VoiceMode] KayÄ±t hatasÄ±: %s", e)
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return None

        if not buffer:
            logger.warning("[VoiceMode] Ses verisi alÄ±namadÄ±.")
            return None

        # Buffer'Ä± numpy array'e Ã§evir
        ses_verisi = np.concatenate(buffer, axis=0)  # type: ignore[arg-type]
        sure = time.monotonic() - baslangic
        self.istatistik["kayit_sayisi"] += 1
        self.istatistik["toplam_konusma_suresi"] += sure

        return SesKaydi(
            veri=ses_verisi,
            ornekleme_hizi=self.ornekleme_hizi,
            sure_sn=sure,
        )

    def _sureli_kaydet(self, sure: float = 0.0) -> Optional[SesKaydi]:
        """Belirtilen sÃ¼re boyunca ses kaydeder.

        Args:
            sure: KayÄ±t sÃ¼resi (saniye). 0 ise varsayÄ±lan kullanÄ±lÄ±r.

        Returns:
            SesKaydi nesnesi veya baÅŸarÄ±sÄ±zsa None.
        """
        if not SD_MEVCUT:
            logger.error("[VoiceMode] sounddevice gerekli â€” kayÄ±t yapÄ±lamaz.")
            return None

        sure = sure or self.kayit_suresi
        self.durum = VoiceModeDurum.DÄ°NLÄ°YOR
        print(f"ğŸ¤ {sure:.0f} saniye kaydediliyor...")

        try:
            ses_verisi = sd.rec(
                int(sure * self.ornekleme_hizi),
                samplerate=self.ornekleme_hizi,
                channels=self.kanal_sayisi,
                device=self.kaynak_id,
            )
            sd.wait()
        except Exception as e:
            logger.error("[VoiceMode] KayÄ±t hatasÄ±: %s", e)
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return None

        self.istatistik["kayit_sayisi"] += 1
        self.istatistik["toplam_konusma_suresi"] += sure

        return SesKaydi(
            veri=ses_verisi,
            ornekleme_hizi=self.ornekleme_hizi,
            sure_sn=sure,
        )

    def kaydet(
        self,
        sure: float = 0.0,
        vad: bool = True,
        maks_sure: float = 30.0,
    ) -> Optional[SesKaydi]:
        """Ses kaydeder.

        VAD (Voice Activity Detection) ile otomatik kesme veya
        sabit sÃ¼reli kayÄ±t yapar.

        Args:
            sure: Sabit sÃ¼re (saniye). 0 ise VAD veya varsayÄ±lan sÃ¼re kullanÄ±lÄ±r.
            vad: VAD kullanÄ±lsÄ±n mÄ±? (varsayÄ±lan: True)
            maks_sure: VAD modunda maksimum kayÄ±t sÃ¼resi.

        Returns:
            SesKaydi nesnesi veya baÅŸarÄ±sÄ±zsa None.
        """
        if vad and sure <= 0:
            return self._vad_ile_kaydet(maks_sure=maks_sure)
        return self._sureli_kaydet(sure=sure or self.kayit_suresi)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # STT â€” KonuÅŸmadan Metne
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _ses_verisini_wav_yap(self, kayit: SesKaydi) -> Optional[str]:
        """NumPy ses verisini geÃ§ici WAV dosyasÄ±na yazar.

        scipy.io.wavfile veya soundfile kullanÄ±r; yoksa elle yazar.

        Args:
            kayit: SesKaydi nesnesi (veri ve ornekleme_hizi ile).

        Returns:
            WAV dosya yolu veya baÅŸarÄ±sÄ±zsa None.
        """
        if kayit.dosya_yolu and os.path.exists(kayit.dosya_yolu):
            return kayit.dosya_yolu

        try:
            # soundfile ile yaz
            import soundfile as sf

            fd, yol = tempfile.mkstemp(suffix=".wav", prefix="reymen_voice_")
            os.close(fd)
            sf.write(yol, kayit.veri, kayit.ornekleme_hizi)
            kayit.dosya_yolu = yol
            return yol
        except ImportError:
            logger.warning("[fix_01_sessiz_except] ImportError")

        try:
            # scipy.io.wavfile ile yaz
            from scipy.io import wavfile

            fd, yol = tempfile.mkstemp(suffix=".wav", prefix="reymen_voice_")
            os.close(fd)
            wavfile.write(yol, kayit.ornekleme_hizi, kayit.veri)
            kayit.dosya_yolu = yol
            return yol
        except ImportError:
            logger.warning("[fix_01_sessiz_except] ImportError")

        logger.error("[VoiceMode] WAV yazmak iÃ§in soundfile veya scipy gerekli.")
        return None

    def _faster_whisper_stt(self, ses_yolu: str) -> str:
        """faster-whisper ile yerel STT Ã§evirisi.

        Args:
            ses_yolu: WAV dosya yolu.

        Returns:
            Ã‡Ã¶zÃ¼mlenen metin.
        """
        if not _FASTER_WHISPER_MEVCUT:
            raise RuntimeError("faster-whisper yÃ¼klÃ¼ deÄŸil.")

        # Modeli ilk Ã§aÄŸrÄ±da yÃ¼kle
        if self._whisper_model is None:
            model_boyutu = self._cfg.get("whisper_model", "tiny")
            device = self._cfg.get("whisper_device", "cpu")
            compute_type = self._cfg.get("whisper_compute", "int8")
            logger.info(
                "[VoiceMode] faster-whisper model yÃ¼kleniyor: %s (%s, %s)...",
                model_boyutu,
                device,
                compute_type,
            )
            self._whisper_model = WhisperModel(
                model_boyutu,
                device=device,
                compute_type=compute_type,
            )

        segmentler, _bilgi = self._whisper_model.transcribe(
            ses_yolu,
            language=self.dil,
            beam_size=5,
        )
        metin = " ".join(seg.text for seg in segmentler).strip()
        return metin

    def _openai_stt(self, ses_yolu: str) -> str:
        """OpenAI Whisper API ile STT Ã§evirisi.

        Args:
            ses_yolu: WAV dosya yolu.

        Returns:
            Ã‡Ã¶zÃ¼mlenen metin.
        """
        if not _OPENAI_MEVCUT:
            raise RuntimeError("openai (OpenAI SDK) yÃ¼klÃ¼ deÄŸil.")

        if self._openai_client is None:
            api_key = self._cfg.get(
                "openai_api_key",
                os.environ.get("OPENAI_API_KEY", ""),
            )
            self._openai_client = OpenAI(api_key=api_key)

        with open(ses_yolu, "rb") as f:
            yanit = self._openai_client.audio.transcriptions.create(
                model=self._cfg.get("openai_stt_model", "whisper-1"),
                file=f,
                language=self.dil,
            )
        return yanit.text.strip()

    def metne_cevir(self, kayit: SesKaydi) -> str:
        """KaydedilmiÅŸ sesi metne Ã§evirir (STT).

        SÄ±rasÄ±yla dener:
            1. SeÃ§ili STT backend (faster-whisper veya openai)
            2. Varsa diÄŸer backend

        Args:
            kayit: SesKaydi nesnesi.

        Returns:
            Ã‡Ã¶zÃ¼mlenen metin veya hata durumunda "[STT HatasÄ±] ...".
        """
        self.durum = VoiceModeDurum.Ä°ÅLÄ°YOR
        print("ğŸ“ Ses metne Ã§evriliyor...")

        # WAV dosyasÄ±na yaz
        ses_yolu = self._ses_verisini_wav_yap(kayit)
        if not ses_yolu:
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return "[STT HatasÄ±] WAV dosyasÄ± oluÅŸturulamadÄ±."

        # STT backend'leri dene
        hatalar: list[str] = []
        backends = [self.stt_backend]
        if self.stt_backend == "faster_whisper":
            backends.append("openai")
        else:
            backends.append("faster_whisper")

        for backend in backends:
            try:
                if backend == "faster_whisper" and _FASTER_WHISPER_MEVCUT:
                    metin = self._faster_whisper_stt(ses_yolu)
                elif backend == "openai" and _OPENAI_MEVCUT:
                    metin = self._openai_stt(ses_yolu)
                else:
                    continue

                if metin:
                    kayit.metin = metin
                    self.istatistik["stt_sayisi"] += 1
                    self.durum = VoiceModeDurum.DURDU
                    # Temp dosyayÄ± temizle
                    self._temizle(ses_yolu)
                    return metin
            except Exception as e:
                hatalar.append(f"{backend}: {e}")
                logger.warning("[VoiceMode] STT backend hatasÄ± (%s): %s", backend, e)
                continue

        self._temizle(ses_yolu)
        self.durum = VoiceModeDurum.HATA
        self.istatistik["hata_sayisi"] += 1
        hata_msg = f"[STT HatasÄ±] TÃ¼m backend'ler baÅŸarÄ±sÄ±z: {'; '.join(hatalar)}"
        logger.error(hata_msg)
        return hata_msg

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # TTS â€” Metinden Sese (edge-tts)
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def seslendir(self, metin: str) -> Optional[bytes]:
        """Metni edge-tts ile seslendirir.

        Args:
            metin: Seslendirilecek metin.

        Returns:
            MP3 ses verisi (bytes) veya baÅŸarÄ±sÄ±zsa None.
        """
        if not _EDGE_TTS_MEVCUT:
            logger.error("[VoiceMode] edge-tts gerekli â€” seslendirme yapÄ±lamaz.")
            return None

        if not metin or not metin.strip():
            logger.warning("[VoiceMode] Seslendirilecek metin boÅŸ.")
            return None

        self.durum = VoiceModeDurum.KONUSUYOR
        print(f"ğŸ—£ Seslendiriliyor ({len(metin)} karakter)...")

        try:
            ses = edge_tts.Communicate(metin.strip(), voice=self.tts_sesi)
            # BytesIO'ya yaz
            buf = io.BytesIO()
            asyncio_loop(self._edge_tts_stream(ses, buf))
            ses_verisi = buf.getvalue()
            self.istatistik["tts_sayisi"] += 1
            return ses_verisi
        except Exception as e:
            logger.error("[VoiceMode] TTS hatasÄ±: %s", e)
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return None

    async def _edge_tts_stream(
        self,
        ses: Any,
        buffer: io.BytesIO,
    ) -> None:
        """edge-tts Ã¼retimini BytesIO buffer'a yazar."""
        async for chunk in ses.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Ses Oynatma
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _pygame_baslat(self) -> bool:
        """Pygame mixer'Ä± baÅŸlatÄ±r (ilk Ã§aÄŸrÄ±da)."""
        if not PYGAME_MEVCUT:
            return False
        if not self._pygame_ilk:
            try:
                pygame.mixer.init(frequency=self.ornekleme_hizi)
                self._pygame_ilk = True
            except Exception as e:
                logger.warning("[VoiceMode] Pygame mixer baÅŸlatÄ±lamadÄ±: %s", e)
                return False
        return True

    def _sounddevice_oynat(self, ses_verisi: bytes, format_hint: str = "mp3") -> None:
        """sounddevice ile ses oynatÄ±r (WAV formatÄ±nda).

        Args:
            ses_verisi: Ses verisi (bytes).
            format_hint: Ses formatÄ± ("mp3" veya "wav").
        """
        if not SD_MEVCUT:
            raise RuntimeError("sounddevice gerekli.")

        # MP3'Ã¼ WAV'a Ã§evir
        if format_hint == "mp3":
            try:
                import pydub
                from pydub import AudioSegment

                ses = AudioSegment.from_mp3(io.BytesIO(ses_verisi))
                wav_buf = io.BytesIO()
                ses.export(wav_buf, format="wav")
                wav_buf.seek(0)
                import soundfile as sf

                data, sr = sf.read(wav_buf)
            except ImportError:
                # pydub yoksa geÃ§ici dosyaya yaz, ffmpeg ile Ã§evir
                fd, temp_in = tempfile.mkstemp(suffix=".mp3", prefix="reymen_tts_")
                os.close(fd)
                with open(temp_in, "wb") as f:
                    f.write(ses_verisi)
                fd, temp_wav = tempfile.mkstemp(suffix=".wav", prefix="reymen_tts_")
                os.close(fd)
                try:
                    subprocess.run(
                        ["ffmpeg", "-y", "-i", temp_in, temp_wav],
                        capture_output=True,
                        timeout=30,
                    )
                    import soundfile as sf

                    data, sr = sf.read(temp_wav)
                except Exception:
                    self._temizle(temp_in)
                    self._temizle(temp_wav)
                    raise
                self._temizle(temp_in)
                self._temizle(temp_wav)
            sound_device_data = data
            sample_rate = sr
        else:
            # WAV direkt
            import soundfile as sf

            data, sr = sf.read(io.BytesIO(ses_verisi))
            sound_device_data = data
            sample_rate = sr

        sd.play(sound_device_data, samplerate=sample_rate)
        sd.wait()

    def _pygame_oynat(self, ses_verisi: bytes) -> None:
        """Pygame ile ses oynatÄ±r.

        Args:
            ses_verisi: MP3 ses verisi (bytes).
        """
        if not self._pygame_baslat():
            raise RuntimeError("Pygame kullanÄ±lamaz.")

        # BytesIO Ã¼zerinden geÃ§ici dosyaya yazmadan oynat
        try:
            # pygame.mixer.music load from file object
            fd, temp = tempfile.mkstemp(suffix=".mp3", prefix="reymen_tts_")
            os.close(fd)
            with open(temp, "wb") as f:
                f.write(ses_verisi)
            pygame.mixer.music.load(temp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self._durdurma_olayi.is_set():
                    pygame.mixer.music.stop()
                    break
                time.sleep(0.1)
            self._temizle(temp)
        except Exception as e:
            logger.warning("[VoiceMode] Pygame oynatma hatasÄ±: %s", e)
            # Fallback: ffplay ile dene
            self._ffplay_oynat(ses_verisi)

    def _ffplay_oynat(self, ses_verisi: bytes) -> None:
        """ffplay (FFmpeg) ile ses oynatÄ±r.

        Args:
            ses_verisi: Ses verisi (bytes).
        """
        if _FFPLAY_BULUNDU is None:
            raise RuntimeError("ffplay bulunamadÄ±.")

        try:
            proc = subprocess.Popen(
                [_FFPLAY_BULUNDU, "-nodisp", "-autoexit", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            proc.stdin.write(ses_verisi)
            proc.stdin.close()
            proc.wait()
        except Exception as e:
            logger.error("[VoiceMode] ffplay oynatma hatasÄ±: %s", e)
            raise

    def oynat(self, ses_verisi: bytes) -> bool:
        """Ses verisini hoparlÃ¶rden oynatÄ±r.

        SÄ±rasÄ±yla dener:
            1. sounddevice (WAV'a Ã§evirerek)
            2. pygame
            3. ffplay

        Args:
            ses_verisi: Ses verisi (bytes, edge-tts'den MP3).

        Returns:
            BaÅŸarÄ±lÄ±ysa True, deÄŸilse False.
        """
        if not ses_verisi:
            return False

        self.durum = VoiceModeDurum.KONUSUYOR
        print("ğŸ”Š OynatÄ±lÄ±yor...")

        hatalar: list[str] = []

        # 1. sounddevice
        if SD_MEVCUT:
            try:
                self._sounddevice_oynat(ses_verisi)
                self.durum = VoiceModeDurum.DURDU
                return True
            except Exception as e:
                hatalar.append(f"sounddevice: {e}")
                logger.debug(
                    "[VoiceMode] sounddevice oynatma baÅŸarÄ±sÄ±z, pygame deneniyor..."
                )

        # 2. pygame
        if PYGAME_MEVCUT:
            try:
                self._pygame_oynat(ses_verisi)
                self.durum = VoiceModeDurum.DURDU
                return True
            except Exception as e:
                hatalar.append(f"pygame: {e}")

        # 3. ffplay
        if _FFPLAY_BULUNDU is not None:
            try:
                self._ffplay_oynat(ses_verisi)
                self.durum = VoiceModeDurum.DURDU
                return True
            except Exception as e:
                hatalar.append(f"ffplay: {e}")

        self.durum = VoiceModeDurum.HATA
        self.istatistik["hata_sayisi"] += 1
        logger.error(
            "[VoiceMode] TÃ¼m oynatma backend'leri baÅŸarÄ±sÄ±z: %s", "; ".join(hatalar)
        )
        return False

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Beyin (LLM) Entegrasyonu
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _beyin_yanit(self, metin: str) -> str:
        """KullanÄ±cÄ± metnini Beyin'e gÃ¶nderir, yanÄ±t alÄ±r.

        Args:
            metin: KullanÄ±cÄ±nÄ±n sÃ¶ylediÄŸi metin.

        Returns:
            Beyin yanÄ±tÄ± metni.
        """
        if self.beyin is None:
            logger.warning("[VoiceMode] Beyin baÄŸlÄ± deÄŸil â€” yanÄ±t Ã¼retilemez.")
            return "[Beyin yok â€” sesli test modu]"

        print("ğŸ§  Beyin dÃ¼ÅŸÃ¼nÃ¼yor...")
        try:
            # VarsayÄ±lan sistem prompt
            sistem = self._cfg.get(
                "sistem_prompt",
                "Sen yardÄ±msever bir asistansÄ±n. KullanÄ±cÄ±yla sesli olarak "
                "TÃ¼rkÃ§e konuÅŸuyorsun. KÄ±sa ve net cevaplar ver.",
            )
            mesajlar = [
                {"role": "user", "content": metin},
            ]
            yanit = self.beyin.dusun(
                sistem_prompt=sistem,
                mesajlar=mesajlar,
            )
            return yanit
        except Exception as e:
            logger.error("[VoiceMode] Beyin hatasÄ±: %s", e)
            self.istatistik["hata_sayisi"] += 1
            return f"[Beyin HatasÄ±] {e}"

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Ana DÃ¶ngÃ¼: Kaydet â†’ STT â†’ LLM â†’ TTS â†’ Oynat
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def dinle_ve_cevapla(
        self,
        sure: float = 0.0,
        vad: bool = True,
        maks_sure: float = 30.0,
    ) -> bool:
        """Tam sesli dÃ¶ngÃ¼: kaydet â†’ STT â†’ LLM â†’ TTS â†’ oynat.

        Args:
            sure: Sabit kayÄ±t sÃ¼resi (0 = VAD veya varsayÄ±lan).
            vad: Voice Activity Detection kullanÄ±lsÄ±n mÄ±?
            maks_sure: VAD'de maksimum kayÄ±t sÃ¼resi.

        Returns:
            DÃ¶ngÃ¼ baÅŸarÄ±yla tamamlandÄ±ysa True.
        """
        if self._durdurma_olayi.is_set():
            return False

        # 1. Kaydet
        kayit = self.kaydet(sure=sure, vad=vad, maks_sure=maks_sure)
        if kayit is None:
            return False

        # 2. STT
        metin = self.metne_cevir(kayit)
        if not metin or metin.startswith("[STT"):
            print(f"âŒ {metin}")
            return False

        print(f"\nğŸ“ SÃ¶ylediÄŸiniz: {metin}")

        # 3. LLM yanÄ±tÄ±
        yanit = self._beyin_yanit(metin)
        if yanit.startswith("[Beyin"):
            print(f"âŒ {yanit}")
            return False

        print(f"ğŸ¤– YanÄ±t: {yanit}")

        # 4. TTS
        ses_verisi = self.seslendir(yanit)
        if ses_verisi is None:
            return False

        # 5. Oynat
        return self.oynat(ses_verisi)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # REPL (Read-Eval-Print-Loop) ArayÃ¼zÃ¼
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def baslat(self) -> None:
        """EtkileÅŸimli sesli REPL baÅŸlatÄ±r.

        Komutlar:
            dinle   â€” konuÅŸmayÄ± dinle ve cevapla (VAD)
            kaydet  â€” sabit sÃ¼re kaydet ve cevapla
            test    â€” ses testi (kaydet â†’ oynat, LLM'siz)
            durum   â€” mevcut durumu gÃ¶ster
            cihaz   â€” ses cihazlarÄ±nÄ± listele
            yardÄ±m  â€” komut listesini gÃ¶ster
            cik     â€” REPL'den Ã§Ä±k
        """
        self._durdurma_olayi.clear()
        print("â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—")
        print("â•‘   ğŸ™  ReYMeN Voice Mode â€” Sesli Asistan   â•‘")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        print("Komutlar: dinle | kaydet | test | durum | cihaz | yardÄ±m | cik")
        print()

        komut_handler: dict[str, Callable[[], bool]] = {
            "dinle": lambda: self.dinle_ve_cevapla(vad=True),
            "kaydet": self._repl_kaydet_ve_cevapla,
            "test": self._repl_ses_testi,
            "durum": self._repl_durum_goster,
            "cihaz": self._repl_cihaz_listele,
            "yardÄ±m": self._repl_yardim,
        }

        try:
            while not self._durdurma_olayi.is_set():
                try:
                    komut = input("\nğŸ™> ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n")
                    break

                if not komut:
                    continue

                if komut == "cik":
                    print("ğŸ‘‹ GÃ¶rÃ¼ÅŸmek Ã¼zere!")
                    break

                handler = komut_handler.get(komut)
                if handler:
                    try:
                        handler()
                    except Exception as e:
                        logger.error("[VoiceMode] Komut hatasÄ±: %s", e)
                        print(f"âŒ Hata: {e}")
                else:
                    print(f"âŒ Bilinmeyen komut: '{komut}'. 'yardÄ±m' yazÄ±n.")
        finally:
            self.durum = VoiceModeDurum.DURDU

    def _repl_kaydet_ve_cevapla(self) -> bool:
        """Sabit sÃ¼reli kayÄ±t + cevaplama (REPL komutu)."""
        try:
            sure_str = input("â± KayÄ±t sÃ¼resi (saniye, varsayÄ±lan 5): ").strip()
            sure = float(sure_str) if sure_str else 5.0
        except (ValueError, EOFError):
            sure = 5.0
        return self.dinle_ve_cevapla(sure=sure, vad=False)

    def _repl_ses_testi(self) -> bool:
        """Ses testi: kaydet â†’ STT â†’ oynat (LLM'siz)."""
        print("ğŸ”Š Ses testi baÅŸlatÄ±lÄ±yor...")
        kayit = self.kaydet(vad=True, maks_sure=10.0)
        if kayit is None:
            print("âŒ KayÄ±t baÅŸarÄ±sÄ±z.")
            return False
        metin = self.metne_cevir(kayit)
        print(f"ğŸ“ AlgÄ±lanan: {metin}")
        # KaydÄ± oynat
        ses_yolu = self._ses_verisini_wav_yap(kayit)
        if ses_yolu:
            with open(ses_yolu, "rb") as f:
                wav_data = f.read()
            self.oynat(wav_data)
            self._temizle(ses_yolu)
        return True

    def _repl_durum_goster(self) -> bool:
        """Mevcut durumu gÃ¶ster (REPL komutu)."""
        durum = self.kullanilabilir_mi()
        print("â•”â•â•â• VoiceMode Durumu â•â•â•â•—")
        print(f"  Durum     : {self.durum}")
        print(f"  Mikrofon  : {'âœ…' if durum['mikrofon'] else 'âŒ'}")
        print(f"  HoparlÃ¶r  : {'âœ…' if durum['hoparlor'] else 'âŒ'}")
        print(f"  STT       : {'âœ…' if durum['stt'] else 'âŒ'}")
        print(f"  TTS       : {'âœ…' if durum['tts'] else 'âŒ'}")
        print(f"  Beyin     : {'âœ…' if durum['beyin'] else 'âŒ'}")
        print(f"  STT Motor : {self.stt_backend}")
        print(f"  TTS Ses   : {self.tts_sesi}")
        print(f"  KayÄ±tlar  : {self.istatistik['kayit_sayisi']}")
        print(f"  STT SayÄ±  : {self.istatistik['stt_sayisi']}")
        print(f"  TTS SayÄ±  : {self.istatistik['tts_sayisi']}")
        print(f"  Hata      : {self.istatistik['hata_sayisi']}")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        return True

    def _repl_cihaz_listele(self) -> bool:
        """Ses cihazlarÄ±nÄ± listele (REPL komutu)."""
        cihazlar = self.cihazlari_listele()
        if not cihazlar:
            print("âŒ Cihaz bulunamadÄ± veya sounddevice yok.")
            return False
        print("â•”â•â•â• Ses CihazlarÄ± â•â•â•â•—")
        for c in cihazlar:
            print(f"  [{c['id']}] {c['adi']}")
            print(f"       Kanal: {c['kanal']}, Ã–rnek: {c['ornek']} Hz")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        return True

    def _repl_yardim(self) -> bool:
        """YardÄ±m mesajÄ± gÃ¶ster (REPL komutu)."""
        print("â•”â•â•â• Komutlar â•â•â•â•—")
        print("  dinle  â€” KonuÅŸmayÄ± dinle (VAD) ve Beyin ile cevapla")
        print("  kaydet â€” Sabit sÃ¼re belirleyip kaydet ve cevapla")
        print("  test   â€” Ses testi (kaydet â†’ Ã§Ã¶z â†’ oynat, LLM'siz)")
        print("  durum  â€” Mevcut yapÄ±landÄ±rma ve kullanÄ±m istatistikleri")
        print("  cihaz  â€” Ses giriÅŸ/Ã§Ä±kÄ±ÅŸ cihazlarÄ±nÄ± listele")
        print("  cik    â€” Ã‡Ä±kÄ±ÅŸ")
        print("  yardÄ±m â€” Bu mesaj")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        return True

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Kontrol / Temizlik
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def durdur(self) -> None:
        """TÃ¼m ses iÅŸlemlerini durdurur."""
        self._durdurma_olayi.set()

        # Pygame oynatma varsa durdur
        if PYGAME_MEVCUT and self._pygame_ilk:
            try:
                pygame.mixer.music.stop()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        # sounddevice oynatma varsa durdur
        if SD_MEVCUT:
            try:
                sd.stop()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")

        self.durum = VoiceModeDurum.DURDU
        logger.info("[VoiceMode] Durduruldu.")

    def temizle(self) -> None:
        """KaynaklarÄ± serbest bÄ±rak."""
        self.durdur()

        # Whisper modelini temizle
        if self._whisper_model is not None:
            try:
                del self._whisper_model
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
            self._whisper_model = None

        # OpenAI client
        self._openai_client = None

        # Pygame mixer
        if PYGAME_MEVCUT and self._pygame_ilk:
            try:
                pygame.mixer.quit()
            except Exception:
                logger.warning("[fix_01_sessiz_except] Exception")
            self._pygame_ilk = False

    @staticmethod
    def _temizle(dosya_yolu: str) -> None:
        """GeÃ§ici dosyayÄ± gÃ¼venle siler."""
        try:
            if dosya_yolu and os.path.exists(dosya_yolu):
                os.unlink(dosya_yolu)
        except Exception as e:
            logger.debug("[VoiceMode] Temp dosya silinemedi: %s â€” %s", dosya_yolu, e)


# â”€â”€ Asenkron yardÄ±mcÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def asyncio_loop(koroutin: Any) -> None:
    """Async fonksiyonu senkron context'te Ã§alÄ±ÅŸtÄ±rÄ±r.

    Mevcut event loop varsa onu kullanÄ±r, yoksa yeni loop oluÅŸturur.

    Args:
        koroutin: Ã‡alÄ±ÅŸtÄ±rÄ±lacak coroutine.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Zaten Ã§alÄ±ÅŸan bir loop var â€” yeni loop aÃ§
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(koroutin)
            finally:
                loop.close()
        else:
            loop.run_until_complete(koroutin)
    except RuntimeError:
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(koroutin)
        finally:
            loop.close()


# â”€â”€ DÄ±ÅŸa aktarÄ±lan isimler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

__all__ = [
    "VoiceMode",
    "VoiceModeDurum",
    "SesKaydi",
]


# â”€â”€ Test / Demo â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    print("VoiceMode Demo")
    print("==============")
    print()

    vm = VoiceMode()
    durum = vm.kullanilabilir_mi()
    print(f"Mikrofon: {'âœ…' if durum['mikrofon'] else 'âŒ'}")
    print(f"HoparlÃ¶r: {'âœ…' if durum['hoparlor'] else 'âŒ'}")
    print(f"STT:      {'âœ…' if durum['stt'] else 'âŒ'}")
    print(f"TTS:      {'âœ…' if durum['tts'] else 'âŒ'}")
    print(f"Beyin:    {'âœ…' if durum['beyin'] else 'âŒ'}")
    print()

    if all(durum.values()):
        print("TÃ¼m bileÅŸenler hazÄ±r. REPL baÅŸlatÄ±lÄ±yor...")
        vm.baslat()
    else:
        print("Demo modu: sadece cihaz listeleme yapÄ±labilir.")
        cihazlar = vm.cihazlari_listele()
        if cihazlar:
            print(f"\n{len(cihazlar)} cihaz bulundu.")
            for c in cihazlar[:5]:
                print(f"  [{c['id']}] {c['adi']}")
