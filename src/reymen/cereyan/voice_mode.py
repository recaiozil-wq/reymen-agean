# -*- coding: utf-8 -*-
"""
voice_mode.py â€” Sesli (Push-to-Talk) aray¼z mod¼l¼.

Mikrofondan ses kaydeder, faster-whisper ile metne §evirir,
Beyin (LLM) ile yanit ¼retir, edge-tts ile seslendirir
ve hoparlsrden oynatir.

Kullanim:
    from reymen.cereyan.voice_mode import VoiceMode

    vm = VoiceMode(beyin=benim_beyin)
    vm.baslat()         # REPL: dinle / konus / cik
    vm.dinle_ve_cevapla()  # tek seferlik kaydet->STT->LLM->TTS dsng¼s¼

Baimliliklar (opsiyonel â€” eksik olanlar graceful degrade yapar):
    - sounddevice       : mikrofon kaydi + hoparlsr oynatma
    - numpy             : ses buffer ilemleri
    - faster-whisper    : yerel STT (CPU/GPU)
    - edge-tts          : Microsoft Edge TTS (¼cretsiz, §evrimi§i)
    - pygame            : alternatif ses oynatici
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

# â”€â”€ Opsiyonel baimliliklar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# sounddevice â€” mikrofon kaydi ve hoparlsr oynatma
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

# pygame â€” alternatif ses oynatici
try:
    import pygame

    PYGAME_MEVCUT = True
except ImportError:
    pygame = None  # type: ignore[assignment]
    PYGAME_MEVCUT = False

# ffmpeg/ffplay â€” ses oynatma i§in sistem araci
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
    """Beyin sinifini dsnd¼r¼r; yoksa None."""
    try:
        from reymen.cereyan.beyin import Beyin

        return Beyin
    except ImportError:
        return None


# â”€â”€ Varsayilan sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_VARSAYILAN_SES_KAYNAGI: int = 0  # varsayilan mikrofon
_VARSAYILAN_ORNEKLEME_HIZI: int = 16000  # Whisper i§in ideal
_VARSAYILAN_KANAL_SAYISI: int = 1  # mono
_VARSAYILAN_KAYIT_SURESI: float = 5.0  # saniye (push-to-talk deilse)
_VARSAYILAN_DINLEME_ESIGI: float = 0.02  # ses seviyesi esigi (VAD basit)
_VARSAYILAN_SESSIZLIK_SURESI: float = 1.5  # VAD i§in sessizlik timeout
_VARSAYILAN_DIL: str = "tr"  # STT dili
_VARSAYILAN_TTS_SESI: str = "tr-TR-AhmetNeural"  # edge-tts T¼rk§e erkek sesi

# VAD (Voice Activity Detection) parametreleri
_VAD_PENCERE_BOYUTU: int = 1024  # RMS penceresi
_VAD_SESSIZ_EN_COK: int = 15  # ka§ sessiz pencereden sonra dur


# â”€â”€ Ses verisi taiyicisi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class SesKaydi:
    """Kaydedilmi ses verisini ve ¼stverisini tair."""

    veri: Optional[Any] = None  # numpy array
    ornekleme_hizi: int = _VARSAYILAN_ORNEKLEME_HIZI
    sure_sn: float = 0.0
    dosya_yolu: Optional[str] = None  # temp wav dosya yolu
    metin: str = ""  # STT §iktisi


# â”€â”€ Durum kodlari â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class VoiceModeDurum:
    """VoiceMode §alima durumlari."""

    DURDU = "durdu"
    DINLIYOR = "dinliyor"
    KONUSUYOR = "konusuyor"
    ILIYOR = "isliyor"
    HATA = "hata"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VoiceMode Ana Sinifi
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class VoiceMode:
    """Sesli aray¼z ysneticisi.

    Push-to-talk ve otomatik VAD ile ses kaydi, STT, LLM yaniti
    ve TTS §iktisini tek bir dsng¼de birletirir.

    Args:
        beyin: Beyin instance'i (LLM balantisi). Yoksa sadece
               kayit + STT + TTS test edilebilir.
        config: Yapilandirma sszl¼¼ (opsiyonel).
            Anahtarlar:
                - kaynak_id: mikrofon cihaz indeksi (int)
                - ornekleme_hizi: srnekleme hizi (int)
                - kayit_suresi: maksimum kayit s¼resi (float)
                - dil: STT dil kodu (str)
                - tts_sesi: edge-tts ses adi (str)
                - stt_backend: "faster_whisper" veya "openai"
                - tts_backend: "edge_tts" (tek se§enek)
                - ses_esii: VAD ses eii (float)
                - sessizlik_suresi: VAD timeout (float)
    """

    def __init__(
        self,
        beyin: Optional[Any] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> None:
        self.beyin = beyin
        self._cfg = config or {}

        # â”€â”€ Cihaz yapilandirmasi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.kaynak_id: int = self._cfg.get("kaynak_id", _VARSAYILAN_SES_KAYNAGI)
        self.ornekleme_hizi: int = self._cfg.get(
            "ornekleme_hizi", _VARSAYILAN_ORNEKLEME_HIZI
        )
        self.kanal_sayisi: int = self._cfg.get("kanal_sayisi", _VARSAYILAN_KANAL_SAYISI)
        self.kayit_suresi: float = self._cfg.get(
            "kayit_suresi", _VARSAYILAN_KAYIT_SURESI
        )

        # â”€â”€ STT yapilandirmasi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.dil: str = self._cfg.get("dil", _VARSAYILAN_DIL)
        self.stt_backend: str = self._cfg.get("stt_backend", "faster_whisper")
        self._whisper_model: Optional[Any] = None
        self._openai_client: Optional[Any] = None

        # â”€â”€ TTS yapilandirmasi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.tts_sesi: str = self._cfg.get("tts_sesi", _VARSAYILAN_TTS_SESI)
        self.tts_backend: str = self._cfg.get("tts_backend", "edge_tts")

        # â”€â”€ VAD yapilandirmasi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.ses_esii: float = self._cfg.get("ses_esii", _VARSAYILAN_DINLEME_ESII)
        self.sessizlik_suresi: float = self._cfg.get(
            "sessizlik_suresi", _VARSAYILAN_SESSIZLIK_SURESI
        )

        # â”€â”€ calima durumu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.durum: str = VoiceModeDurum.DURDU
        self._durdurma_olayi = threading.Event()
        self._kilit = threading.Lock()

        # â”€â”€ Ses oynatma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self._pygame_ilk = False

        # â”€â”€ Istatistik â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        self.istatistik: dict[str, Any] = {
            "kayit_sayisi": 0,
            "stt_sayisi": 0,
            "tts_sayisi": 0,
            "hata_sayisi": 0,
            "toplam_konusma_suresi": 0.0,
        }

        # Balangi§ta kullanilabilirlii kontrol et
        self._kullanilabilirlik_kontrol()

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Kontrol
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _kullanilabilirlik_kontrol(self) -> None:
        """Mevcut baimliliklari raporla."""
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
                "[VoiceMode] Eksik baimliliklar: %s",
                ", ".join(eksik),
            )

    def kullanilabilir_mi(self) -> dict[str, bool]:
        """Kullanilabilirlik durumunu sszl¼k olarak dsnd¼r¼r.

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
    # Mikrofon â€” Ses Kaydi
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def cihazlari_listele(self) -> list[dict[str, Any]]:
        """Kullanilabilir ses cihazlarini listeler.

        Returns:
            Her cihaz i§in {'id': int, 'adi': str, 'kanal': int, 'ornek': int}
            listesi. sounddevice yoksa bo liste.
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
            logger.error("[VoiceMode] Cihaz listeleme hatasi: %s", e)
            return []

    def _vad_ile_kaydet(
        self,
        maks_sure: float = 30.0,
    ) -> Optional[SesKaydi]:
        """Voice Activity Detection ile konuma algilayarak kaydeder.

        Sessizlik algilandiinda veya maksimum s¼re aildiinda durur.

        Args:
            maks_sure: Maksimum kayit s¼resi (saniye).

        Returns:
            SesKaydi nesnesi veya baarisizsa None.
        """
        if not SD_MEVCUT:
            logger.error("[VoiceMode] sounddevice gerekli â€” VAD kaydi yapilamaz.")
            return None

        self.durum = VoiceModeDurum.DINLIYOR
        print("ğ¤ Dinliyor (konumayi birakinca otomatik durur)...")

        buffer: list = []
        sessiz_sayac = 0
        baslangic = time.monotonic()

        def _callback(indata: Any, frames: int, _time_info: Any, status: Any) -> None:
            nonlocal sessiz_sayac
            if status:
                logger.debug("[VoiceMode] Ses akii status: %s", status)
            # RMS ses seviyesi
            rms = np.sqrt(np.mean(indata**2))  # type: ignore[operator]
            buffer.append(indata.copy())
            if rms < self.ses_esii:
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
                        print("\nâ¹ Durduruldu.")
                        return None
                    if sessiz_sayac > _VAD_SESSIZ_EN_COK:
                        print()  # yeni satir
                        break
                    if time.monotonic() - baslangic > maks_sure:
                        print("\nâi Maksimum s¼re aildi.")
                        break
                    time.sleep(0.05)
        except Exception as e:
            logger.error("[VoiceMode] Kayit hatasi: %s", e)
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return None

        if not buffer:
            logger.warning("[VoiceMode] Ses verisi alinamadi.")
            return None

        # Buffer'i numpy array'e §evir
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
        """Belirtilen s¼re boyunca ses kaydeder.

        Args:
            sure: Kayit s¼resi (saniye). 0 ise varsayilan kullanilir.

        Returns:
            SesKaydi nesnesi veya baarisizsa None.
        """
        if not SD_MEVCUT:
            logger.error("[VoiceMode] sounddevice gerekli â€” kayit yapilamaz.")
            return None

        sure = sure or self.kayit_suresi
        self.durum = VoiceModeDurum.DINLIYOR
        print(f"ğ¤ {sure:.0f} saniye kaydediliyor...")

        try:
            ses_verisi = sd.rec(
                int(sure * self.ornekleme_hizi),
                samplerate=self.ornekleme_hizi,
                channels=self.kanal_sayisi,
                device=self.kaynak_id,
            )
            sd.wait()
        except Exception as e:
            logger.error("[VoiceMode] Kayit hatasi: %s", e)
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
        sabit s¼reli kayit yapar.

        Args:
            sure: Sabit s¼re (saniye). 0 ise VAD veya varsayilan s¼re kullanilir.
            vad: VAD kullanilsin mi? (varsayilan: True)
            maks_sure: VAD modunda maksimum kayit s¼resi.

        Returns:
            SesKaydi nesnesi veya baarisizsa None.
        """
        if vad and sure <= 0:
            return self._vad_ile_kaydet(maks_sure=maks_sure)
        return self._sureli_kaydet(sure=sure or self.kayit_suresi)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # STT â€” Konumadan Metne
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _ses_verisini_wav_yap(self, kayit: SesKaydi) -> Optional[str]:
        """NumPy ses verisini ge§ici WAV dosyasina yazar.

        scipy.io.wavfile veya soundfile kullanir; yoksa elle yazar.

        Args:
            kayit: SesKaydi nesnesi (veri ve ornekleme_hizi ile).

        Returns:
            WAV dosya yolu veya baarisizsa None.
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

        logger.error("[VoiceMode] WAV yazmak i§in soundfile veya scipy gerekli.")
        return None

    def _faster_whisper_stt(self, ses_yolu: str) -> str:
        """faster-whisper ile yerel STT §evirisi.

        Args:
            ses_yolu: WAV dosya yolu.

        Returns:
            csz¼mlenen metin.
        """
        if not _FASTER_WHISPER_MEVCUT:
            raise RuntimeError("faster-whisper y¼kl¼ deil.")

        # Modeli ilk §arida y¼kle
        if self._whisper_model is None:
            model_boyutu = self._cfg.get("whisper_model", "tiny")
            device = self._cfg.get("whisper_device", "cpu")
            compute_type = self._cfg.get("whisper_compute", "int8")
            logger.info(
                "[VoiceMode] faster-whisper model y¼kleniyor: %s (%s, %s)...",
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
        """OpenAI Whisper API ile STT §evirisi.

        Args:
            ses_yolu: WAV dosya yolu.

        Returns:
            csz¼mlenen metin.
        """
        if not _OPENAI_MEVCUT:
            raise RuntimeError("openai (OpenAI SDK) y¼kl¼ deil.")

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
        """Kaydedilmi sesi metne §evirir (STT).

        Sirasiyla dener:
            1. Se§ili STT backend (faster-whisper veya openai)
            2. Varsa dier backend

        Args:
            kayit: SesKaydi nesnesi.

        Returns:
            csz¼mlenen metin veya hata durumunda "[STT Hatasi] ...".
        """
        self.durum = VoiceModeDurum.ILIYOR
        print("ğ“ Ses metne §evriliyor...")

        # WAV dosyasina yaz
        ses_yolu = self._ses_verisini_wav_yap(kayit)
        if not ses_yolu:
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return "[STT Hatasi] WAV dosyasi oluturulamadi."

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
                    # Temp dosyayi temizle
                    self._temizle(ses_yolu)
                    return metin
            except Exception as e:
                hatalar.append(f"{backend}: {e}")
                logger.warning("[VoiceMode] STT backend hatasi (%s): %s", backend, e)
                continue

        self._temizle(ses_yolu)
        self.durum = VoiceModeDurum.HATA
        self.istatistik["hata_sayisi"] += 1
        hata_msg = f"[STT Hatasi] T¼m backend'ler baarisiz: {'; '.join(hatalar)}"
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
            MP3 ses verisi (bytes) veya baarisizsa None.
        """
        if not _EDGE_TTS_MEVCUT:
            logger.error("[VoiceMode] edge-tts gerekli â€” seslendirme yapilamaz.")
            return None

        if not metin or not metin.strip():
            logger.warning("[VoiceMode] Seslendirilecek metin bo.")
            return None

        self.durum = VoiceModeDurum.KONUSUYOR
        print(f"ğ-£ Seslendiriliyor ({len(metin)} karakter)...")

        try:
            ses = edge_tts.Communicate(metin.strip(), voice=self.tts_sesi)
            # BytesIO'ya yaz
            buf = io.BytesIO()
            asyncio_loop(self._edge_tts_stream(ses, buf))
            ses_verisi = buf.getvalue()
            self.istatistik["tts_sayisi"] += 1
            return ses_verisi
        except Exception as e:
            logger.error("[VoiceMode] TTS hatasi: %s", e)
            self.durum = VoiceModeDurum.HATA
            self.istatistik["hata_sayisi"] += 1
            return None

    async def _edge_tts_stream(
        self,
        ses: Any,
        buffer: io.BytesIO,
    ) -> None:
        """edge-tts ¼retimini BytesIO buffer'a yazar."""
        async for chunk in ses.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Ses Oynatma
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _pygame_baslat(self) -> bool:
        """Pygame mixer'i balatir (ilk §arida)."""
        if not PYGAME_MEVCUT:
            return False
        if not self._pygame_ilk:
            try:
                pygame.mixer.init(frequency=self.ornekleme_hizi)
                self._pygame_ilk = True
            except Exception as e:
                logger.warning("[VoiceMode] Pygame mixer balatilamadi: %s", e)
                return False
        return True

    def _sounddevice_oynat(self, ses_verisi: bytes, format_hint: str = "mp3") -> None:
        """sounddevice ile ses oynatir (WAV formatinda).

        Args:
            ses_verisi: Ses verisi (bytes).
            format_hint: Ses formati ("mp3" veya "wav").
        """
        if not SD_MEVCUT:
            raise RuntimeError("sounddevice gerekli.")

        # MP3'¼ WAV'a §evir
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
                # pydub yoksa ge§ici dosyaya yaz, ffmpeg ile §evir
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
        """Pygame ile ses oynatir.

        Args:
            ses_verisi: MP3 ses verisi (bytes).
        """
        if not self._pygame_baslat():
            raise RuntimeError("Pygame kullanilamaz.")

        # BytesIO ¼zerinden ge§ici dosyaya yazmadan oynat
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
            logger.warning("[VoiceMode] Pygame oynatma hatasi: %s", e)
            # Fallback: ffplay ile dene
            self._ffplay_oynat(ses_verisi)

    def _ffplay_oynat(self, ses_verisi: bytes) -> None:
        """ffplay (FFmpeg) ile ses oynatir.

        Args:
            ses_verisi: Ses verisi (bytes).
        """
        if _FFPLAY_BULUNDU is None:
            raise RuntimeError("ffplay bulunamadi.")

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
            logger.error("[VoiceMode] ffplay oynatma hatasi: %s", e)
            raise

    def oynat(self, ses_verisi: bytes) -> bool:
        """Ses verisini hoparlsrden oynatir.

        Sirasiyla dener:
            1. sounddevice (WAV'a §evirerek)
            2. pygame
            3. ffplay

        Args:
            ses_verisi: Ses verisi (bytes, edge-tts'den MP3).

        Returns:
            Baariliysa True, deilse False.
        """
        if not ses_verisi:
            return False

        self.durum = VoiceModeDurum.KONUSUYOR
        print("ğ”Š Oynatiliyor...")

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
                    "[VoiceMode] sounddevice oynatma baarisiz, pygame deneniyor..."
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
            "[VoiceMode] T¼m oynatma backend'leri baarisiz: %s", "; ".join(hatalar)
        )
        return False

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Beyin (LLM) Entegrasyonu
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _beyin_yanit(self, metin: str) -> str:
        """Kullanici metnini Beyin'e gsnderir, yanit alir.

        Args:
            metin: Kullanicinin ssyledii metin.

        Returns:
            Beyin yaniti metni.
        """
        if self.beyin is None:
            logger.warning("[VoiceMode] Beyin bali deil â€” yanit ¼retilemez.")
            return "[Beyin yok â€” sesli test modu]"

        print("ğ§  Beyin d¼¼n¼yor...")
        try:
            # Varsayilan sistem prompt
            sistem = self._cfg.get(
                "sistem_prompt",
                "Sen yardimsever bir asistansin. Kullaniciyla sesli olarak "
                "T¼rk§e konuuyorsun. Kisa ve net cevaplar ver.",
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
            logger.error("[VoiceMode] Beyin hatasi: %s", e)
            self.istatistik["hata_sayisi"] += 1
            return f"[Beyin Hatasi] {e}"

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Ana Dsng¼: Kaydet âc’ STT âc’ LLM âc’ TTS âc’ Oynat
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def dinle_ve_cevapla(
        self,
        sure: float = 0.0,
        vad: bool = True,
        maks_sure: float = 30.0,
    ) -> bool:
        """Tam sesli dsng¼: kaydet âc’ STT âc’ LLM âc’ TTS âc’ oynat.

        Args:
            sure: Sabit kayit s¼resi (0 = VAD veya varsayilan).
            vad: Voice Activity Detection kullanilsin mi?
            maks_sure: VAD'de maksimum kayit s¼resi.

        Returns:
            Dsng¼ baariyla tamamlandiysa True.
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

        print(f"\nğ“ Ssylediiniz: {metin}")

        # 3. LLM yaniti
        yanit = self._beyin_yanit(metin)
        if yanit.startswith("[Beyin"):
            print(f"âŒ {yanit}")
            return False

        print(f"ğ¤- Yanit: {yanit}")

        # 4. TTS
        ses_verisi = self.seslendir(yanit)
        if ses_verisi is None:
            return False

        # 5. Oynat
        return self.oynat(ses_verisi)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # REPL (Read-Eval-Print-Loop) Aray¼z¼
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def baslat(self) -> None:
        """Etkileimli sesli REPL balatir.

        Komutlar:
            dinle   â€” konumayi dinle ve cevapla (VAD)
            kaydet  â€” sabit s¼re kaydet ve cevapla
            test    â€” ses testi (kaydet âc’ oynat, LLM'siz)
            durum   â€” mevcut durumu gsster
            cihaz   â€” ses cihazlarini listele
            yardim  â€” komut listesini gsster
            cik     â€” REPL'den §ik
        """
        self._durdurma_olayi.clear()
        print("â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•-")
        print("â•‘   ğS  ReYMeN Voice Mode â€” Sesli Asistan   â•‘")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        print("Komutlar: dinle | kaydet | test | durum | cihaz | yardim | cik")
        print()

        komut_handler: dict[str, Callable[[], bool]] = {
            "dinle": lambda: self.dinle_ve_cevapla(vad=True),
            "kaydet": self._repl_kaydet_ve_cevapla,
            "test": self._repl_ses_testi,
            "durum": self._repl_durum_goster,
            "cihaz": self._repl_cihaz_listele,
            "yardim": self._repl_yardim,
        }

        try:
            while not self._durdurma_olayi.is_set():
                try:
                    komut = input("\nğS> ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n")
                    break

                if not komut:
                    continue

                if komut == "cik":
                    print("ğ‘‹ Gsr¼mek ¼zere!")
                    break

                handler = komut_handler.get(komut)
                if handler:
                    try:
                        handler()
                    except Exception as e:
                        logger.error("[VoiceMode] Komut hatasi: %s", e)
                        print(f"âŒ Hata: {e}")
                else:
                    print(f"âŒ Bilinmeyen komut: '{komut}'. 'yardim' yazin.")
        finally:
            self.durum = VoiceModeDurum.DURDU

    def _repl_kaydet_ve_cevapla(self) -> bool:
        """Sabit s¼reli kayit + cevaplama (REPL komutu)."""
        try:
            sure_str = input("âi Kayit s¼resi (saniye, varsayilan 5): ").strip()
            sure = float(sure_str) if sure_str else 5.0
        except (ValueError, EOFError):
            sure = 5.0
        return self.dinle_ve_cevapla(sure=sure, vad=False)

    def _repl_ses_testi(self) -> bool:
        """Ses testi: kaydet âc’ STT âc’ oynat (LLM'siz)."""
        print("ğ”Š Ses testi balatiliyor...")
        kayit = self.kaydet(vad=True, maks_sure=10.0)
        if kayit is None:
            print("âŒ Kayit baarisiz.")
            return False
        metin = self.metne_cevir(kayit)
        print(f"ğ“ Algilanan: {metin}")
        # Kaydi oynat
        ses_yolu = self._ses_verisini_wav_yap(kayit)
        if ses_yolu:
            with open(ses_yolu, "rb") as f:
                wav_data = f.read()
            self.oynat(wav_data)
            self._temizle(ses_yolu)
        return True

    def _repl_durum_goster(self) -> bool:
        """Mevcut durumu gsster (REPL komutu)."""
        durum = self.kullanilabilir_mi()
        print("â•”â•â•â• VoiceMode Durumu â•â•â•â•-")
        print(f"  Durum     : {self.durum}")
        print(f"  Mikrofon  : {'âœ…' if durum['mikrofon'] else 'âŒ'}")
        print(f"  Hoparlsr  : {'âœ…' if durum['hoparlor'] else 'âŒ'}")
        print(f"  STT       : {'âœ…' if durum['stt'] else 'âŒ'}")
        print(f"  TTS       : {'âœ…' if durum['tts'] else 'âŒ'}")
        print(f"  Beyin     : {'âœ…' if durum['beyin'] else 'âŒ'}")
        print(f"  STT Motor : {self.stt_backend}")
        print(f"  TTS Ses   : {self.tts_sesi}")
        print(f"  Kayitlar  : {self.istatistik['kayit_sayisi']}")
        print(f"  STT Sayi  : {self.istatistik['stt_sayisi']}")
        print(f"  TTS Sayi  : {self.istatistik['tts_sayisi']}")
        print(f"  Hata      : {self.istatistik['hata_sayisi']}")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        return True

    def _repl_cihaz_listele(self) -> bool:
        """Ses cihazlarini listele (REPL komutu)."""
        cihazlar = self.cihazlari_listele()
        if not cihazlar:
            print("âŒ Cihaz bulunamadi veya sounddevice yok.")
            return False
        print("â•”â•â•â• Ses Cihazlari â•â•â•â•-")
        for c in cihazlar:
            print(f"  [{c['id']}] {c['adi']}")
            print(f"       Kanal: {c['kanal']}, -rnek: {c['ornek']} Hz")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        return True

    def _repl_yardim(self) -> bool:
        """Yardim mesaji gsster (REPL komutu)."""
        print("â•”â•â•â• Komutlar â•â•â•â•-")
        print("  dinle  â€” Konumayi dinle (VAD) ve Beyin ile cevapla")
        print("  kaydet â€” Sabit s¼re belirleyip kaydet ve cevapla")
        print("  test   â€” Ses testi (kaydet âc’ §sz âc’ oynat, LLM'siz)")
        print("  durum  â€” Mevcut yapilandirma ve kullanim istatistikleri")
        print("  cihaz  â€” Ses giri/§iki cihazlarini listele")
        print("  cik    â€” ciki")
        print("  yardim â€” Bu mesaj")
        print("â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
        return True

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # Kontrol / Temizlik
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def durdur(self) -> None:
        """T¼m ses ilemlerini durdurur."""
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
        """Kaynaklari serbest birak."""
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
        """Ge§ici dosyayi g¼venle siler."""
        try:
            if dosya_yolu and os.path.exists(dosya_yolu):
                os.unlink(dosya_yolu)
        except Exception as e:
            logger.debug("[VoiceMode] Temp dosya silinemedi: %s â€” %s", dosya_yolu, e)


# â”€â”€ Asenkron yardimci â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def asyncio_loop(koroutin: Any) -> None:
    """Async fonksiyonu senkron context'te §alitirir.

    Mevcut event loop varsa onu kullanir, yoksa yeni loop oluturur.

    Args:
        koroutin: calitirilacak coroutine.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Zaten §alian bir loop var â€” yeni loop a§
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


# â”€â”€ Dia aktarilan isimler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

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
    print(f"Hoparlsr: {'âœ…' if durum['hoparlor'] else 'âŒ'}")
    print(f"STT:      {'âœ…' if durum['stt'] else 'âŒ'}")
    print(f"TTS:      {'âœ…' if durum['tts'] else 'âŒ'}")
    print(f"Beyin:    {'âœ…' if durum['beyin'] else 'âŒ'}")
    print()

    if all(durum.values()):
        print("T¼m bileenler hazir. REPL balatiliyor...")
        vm.baslat()
    else:
        print("Demo modu: sadece cihaz listeleme yapilabilir.")
        cihazlar = vm.cihazlari_listele()
        if cihazlar:
            print(f"\n{len(cihazlar)} cihaz bulundu.")
            for c in cihazlar[:5]:
                print(f"  [{c['id']}] {c['adi']}")
