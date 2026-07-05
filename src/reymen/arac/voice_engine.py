# -*- coding: utf-8 -*-
"""
voice_engine.py â€” Ã‡ok back-end'li ses motoru (ABC tabanlÄ±).

VoiceEngine ABC:
  - Soyut seslendir(text, voice) â†’ str (ses dosyasÄ± yolu)
  - Soyut yaziya_cevir(ses_dosyasi) â†’ str (metin)

Engine'ler:
  - OpenAITTS    â€” OpenAI TTS API (OPENAI_API_KEY ortam deÄŸiÅŸkeni)
  - EdgeTTS      â€” edge-tts (yerel, Ã¼cretsiz, internet gerekli)
  - WhisperSTT   â€” OpenAI Whisper API (ses â†’ yazÄ±, OPENAI_API_KEY gerekli)
  - StubVoice    â€” local dummy (baÄŸÄ±mlÄ±lÄ±k gerektirmez, simÃ¼le eder)

VoiceRegistry:
  - engine kaydet / seÃ§ (ad ile) / seslendir / yaziya_cevir
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

log = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Sabitler
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

_OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"
_OPENAI_STT_URL = "https://api.openai.com/v1/audio/transcriptions"
_USER_AGENT = "ReYMeN-Ajan/1.0"

# OpenAI TTS'de desteklenen sesler
_OPENAI_SESLER = {"alloy", "echo", "fable", "onyx", "nova", "shimmer"}

# VarsayÄ±lan Ã§Ä±ktÄ± dizini
_VOICE_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "output", "voice"
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# YardÄ±mcÄ± fonksiyonlar
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def _cikti_dizini() -> str:
    """Ses dosyalarÄ± iÃ§in Ã§Ä±ktÄ± dizinini oluÅŸtur ve dÃ¶ndÃ¼r."""
    out_dir = _VOICE_OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def _ses_dosyasi_adi(prefix: str = "ses", ext: str = ".mp3") -> str:
    """Benzersiz ses dosyasÄ± adÄ± oluÅŸtur."""
    return os.path.join(_cikti_dizini(), f"{prefix}_{uuid.uuid4().hex[:8]}{ext}")


def _get_openai_api_key() -> str:
    """OPENAI_API_KEY ortam deÄŸiÅŸkenini dÃ¶ndÃ¼r."""
    return os.environ.get("OPENAI_API_KEY", "").strip()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Soyut Taban SÄ±nÄ±fÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class VoiceEngine(ABC):
    """TÃ¼m ses engine'leri iÃ§in soyut taban sÄ±nÄ±fÄ±."""

    @property
    @abstractmethod
    def ad(self) -> str:
        """Engine'in benzersiz adÄ± (kÃ¼Ã§Ã¼k harf)."""
        ...

    @abstractmethod
    def seslendir(self, text: str, voice: str = "alloy") -> str:
        """Metni sese Ã§evir, ses dosyasÄ± yolunu dÃ¶ndÃ¼r."""
        ...

    @abstractmethod
    def yaziya_cevir(self, ses_dosyasi: str) -> str:
        """Ses dosyasÄ±nÄ± metne Ã§evir, metni dÃ¶ndÃ¼r."""
        ...

    def __init__(self) -> None:
        self._hazir = self._bagimliliklari_kontrol_et()

    def _bagimliliklari_kontrol_et(self) -> bool:
        return True

    @property
    def hazir(self) -> bool:
        return self._hazir


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# OpenAI TTS Engine
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class OpenAITTS(VoiceEngine):
    """OpenAI TTS API ile metni sese Ã§evirir. OPENAI_API_KEY ortam deÄŸiÅŸkeni gerekli.

    Desteklenen sesler: alloy, echo, fable, onyx, nova, shimmer
    Model: tts-1 (varsayÄ±lan) veya tts-1-hd
    """

    def __init__(self, model: str = "tts-1") -> None:
        self._model = model
        super().__init__()

    @property
    def ad(self) -> str:
        return "openai"

    def _bagimliliklari_kontrol_et(self) -> bool:
        return bool(_get_openai_api_key())

    def seslendir(self, text: str, voice: str = "alloy") -> str:
        """Metni OpenAI TTS ile sese Ã§evir.

        Args:
            text: Seslendirilecek metin.
            voice: Ses (alloy, echo, fable, onyx, nova, shimmer).

        Returns:
            Ses dosyasÄ±nÄ±n yolu veya hata mesajÄ±.
        """
        api_key = _get_openai_api_key()
        if not api_key:
            return "[SESLENDIR/OpenAI] Hata: OPENAI_API_KEY tanimli degil."

        if not text or not text.strip():
            return "[SESLENDIR/OpenAI] Hata: 'text' bos olamaz."

        ses = voice.strip().lower()
        if ses not in _OPENAI_SESLER:
            ses = "alloy"

        try:
            import urllib.request as _req

            payload = {
                "model": self._model,
                "input": text.strip(),
                "voice": ses,
                "response_format": "mp3",
            }

            data = json.dumps(payload).encode()
            req = _req.Request(
                _OPENAI_TTS_URL,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": _USER_AGENT,
                },
            )

            cikti = _ses_dosyasi_adi(prefix="openai_tts", ext=".mp3")
            with _req.urlopen(req, timeout=60) as r:
                with open(cikti, "wb") as f:
                    f.write(r.read())

            log.info("[OpenAITTS] Ses dosyasi olusturuldu: %s (voice=%s)", cikti, ses)
            return cikti

        except Exception as e:
            log.exception("[OpenAITTS] OpenAI TTS hatasi:")
            import urllib.error as _ue

            if hasattr(e, "read"):
                try:
                    govde = e.read().decode(errors="replace")[:300]
                    return f"[SESLENDIR/OpenAI] HTTP hatasi: {govde}"
                except Exception as _e:
                    __import__("logging").getLogger(__name__).warning(
                        "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                    )
            return f"[SESLENDIR/OpenAI] Hata: {e}"

    def yaziya_cevir(self, ses_dosyasi: str) -> str:
        """Ses dosyasÄ±nÄ± OpenAI Whisper ile metne Ã§evir.

        Not: OpenAITTS engine'i STT iÃ§in deÄŸil TTS iÃ§indir.
        WhisperSTT engine'ini kullanÄ±n.
        """
        return "[SESLENDIR/OpenAI] Bu engine TTS icindir. STT icin WhisperSTT kullanin."


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Edge TTS Engine
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class EdgeTTS(VoiceEngine):
    """Microsoft Edge TTS ile metni sese Ã§evirir (yerel, Ã¼cretsiz, internet gerekli).

    edge-tts pip paketi veya edge-tts CLI kullanÄ±r.
    Desteklenen sesler Microsoft Edge tarafÄ±ndan belirlenir.
    VarsayÄ±lan ses: tr-TR-AhmetNeural (TÃ¼rkÃ§e erkek)
    """

    @property
    def ad(self) -> str:
        return "edge"

    def _bagimliliklari_kontrol_et(self) -> bool:
        """edge-tts kullanÄ±labilir mi kontrol et."""
        try:
            import edge_tts  # noqa: F401

            return True
        except ImportError:
            # CLI kontrolÃ¼
            import shutil

            return shutil.which("edge-tts") is not None

    def seslendir(self, text: str, voice: str = "tr-TR-AhmetNeural") -> str:
        """Metni Edge TTS ile sese Ã§evir.

        Args:
            text: Seslendirilecek metin.
            voice: Edge TTS ses adÄ± (Ã¶rn. tr-TR-AhmetNeural, en-US-AriaNeural).

        Returns:
            Ses dosyasÄ±nÄ±n yolu veya hata mesajÄ±.
        """
        if not text or not text.strip():
            return "[SESLENDIR/Edge] Hata: 'text' bos olamaz."

        if not self._hazir:
            return "[SESLENDIR/Edge] Hata: edge-tts kurulu degil."

        ses = voice.strip() or "tr-TR-AhmetNeural"
        cikti = _ses_dosyasi_adi(prefix="edge_tts", ext=".mp3")

        try:
            # edge-tts kÃ¼tÃ¼phane API'sini dene
            import edge_tts as _edge_tts
            import asyncio

            async def _tts():
                communicate = _edge_tts.Communicate(text.strip(), ses)
                await communicate.save(cikti)

            asyncio.run(_tts())
            log.info("[EdgeTTS] Ses dosyasi olusturuldu: %s (voice=%s)", cikti, ses)
            return cikti

        except ImportError:
            # CLI ile dene
            import subprocess

            try:
                subprocess.run(
                    [
                        "edge-tts",
                        "--text",
                        text.strip(),
                        "--voice",
                        ses,
                        "--write-media",
                        cikti,
                    ],
                    capture_output=True,
                    timeout=60,
                    check=True,
                )
                log.info(
                    "[EdgeTTS] Ses dosyasi olusturuldu (CLI): %s (voice=%s)", cikti, ses
                )
                return cikti
            except subprocess.CalledProcessError as e:
                return f"[SESLENDIR/Edge] CLI hatasi: {e.stderr.decode(errors='replace')[:300]}"
            except FileNotFoundError:
                return "[SESLENDIR/Edge] Hata: edge-tts CLI bulunamadi."
            except Exception as e:
                return f"[SESLENDIR/Edge] CLI hatasi: {e}"

        except Exception as e:
            log.exception("[EdgeTTS] Edge TTS hatasi:")
            return f"[SESLENDIR/Edge] Hata: {e}"

    def yaziya_cevir(self, ses_dosyasi: str) -> str:
        """Edge TTS STT desteklemez."""
        return "[SESLENDIR/Edge] Bu engine TTS icindir, STT desteklemez."


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Whisper STT Engine
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class WhisperSTT(VoiceEngine):
    """OpenAI Whisper API ile ses dosyasÄ±nÄ± metne Ã§evirir.

    OPENAI_API_KEY ortam deÄŸiÅŸkeni gerekli.
    Model: whisper-1 (varsayÄ±lan)
    Desteklenen formatlar: mp3, mp4, mpeg, mpga, m4a, wav, webm
    """

    def __init__(self, model: str = "whisper-1") -> None:
        self._model = model
        super().__init__()

    @property
    def ad(self) -> str:
        return "whisper"

    def _bagimliliklari_kontrol_et(self) -> bool:
        return bool(_get_openai_api_key())

    def seslendir(self, text: str, voice: str = "alloy") -> str:
        """Whisper STT metin Ã¼retir, ses Ã¼retmez."""
        return "[YAZIYA_CEVIR/Whisper] Bu engine STT icindir. TTS icin OpenAITTS veya EdgeTTS kullanin."

    def yaziya_cevir(self, ses_dosyasi: str) -> str:
        """Ses dosyasÄ±nÄ± OpenAI Whisper ile metne Ã§evir.

        Args:
            ses_dosyasi: Ses dosyasÄ±nÄ±n yolu (.mp3, .wav, .m4a, vb.).

        Returns:
            Ã‡evrilen metin veya hata mesajÄ±.
        """
        api_key = _get_openai_api_key()
        if not api_key:
            return "[YAZIYA_CEVIR/Whisper] Hata: OPENAI_API_KEY tanimli degil."

        if not ses_dosyasi or not os.path.isfile(ses_dosyasi):
            return f"[YAZIYA_CEVIR/Whisper] Hata: dosya bulunamadi: {ses_dosyasi}"

        try:
            import urllib.request as _req

            # Multipart form-data ile dosya gÃ¶nder
            boundary = "----WebKitFormBoundary" + uuid.uuid4().hex

            # Dosya iÃ§eriÄŸini oku
            with open(ses_dosyasi, "rb") as f:
                file_data = f.read()

            dosya_adi = os.path.basename(ses_dosyasi)

            # Multipart body oluÅŸtur
            body_parts = []
            # model field
            body_parts.append(f"--{boundary}\r\n")
            body_parts.append('Content-Disposition: form-data; name="model"\r\n\r\n')
            body_parts.append(f"{self._model}\r\n")
            # file field
            body_parts.append(f"--{boundary}\r\n")
            body_parts.append(
                f'Content-Disposition: form-data; name="file"; filename="{dosya_adi}"\r\n'
            )
            body_parts.append("Content-Type: audio/mpeg\r\n\r\n")
            body_parts.append(
                file_data.decode("latin-1")
            )  # binary'yi latin-1 ile gÃ¼venli taÅŸÄ±
            body_parts.append(f"\r\n--{boundary}--\r\n")

            body = ""
            for p in body_parts:
                if isinstance(p, bytes):
                    body += p.decode("latin-1")
                else:
                    body += p

            data = body.encode("latin-1")

            req = _req.Request(
                _OPENAI_STT_URL,
                data=data,
                headers={
                    "Content-Type": f"multipart/form-data; boundary={boundary}",
                    "Authorization": f"Bearer {api_key}",
                    "User-Agent": _USER_AGENT,
                },
            )

            with _req.urlopen(req, timeout=120) as r:
                response = json.loads(r.read().decode())

            metin = response.get("text", "").strip()
            if not metin:
                return "[YAZIYA_CEVIR/Whisper] Hata: metin bulunamadi."

            log.info(
                "[WhisperSTT] Ses dosyasi cozuldu: %s (%d karakter)",
                ses_dosyasi,
                len(metin),
            )
            return metin

        except ImportError:
            # openai kÃ¼tÃ¼phanesini dene
            try:
                from openai import OpenAI

                client = OpenAI(api_key=api_key)
                with open(ses_dosyasi, "rb") as f:
                    transcript = client.audio.transcriptions.create(
                        model=self._model,
                        file=f,
                    )
                metin = transcript.text.strip()
                if not metin:
                    return "[YAZIYA_CEVIR/Whisper] Hata: metin bulunamadi."
                log.info(
                    "[WhisperSTT] Ses dosyasi cozuldu (openai lib): %s (%d karakter)",
                    ses_dosyasi,
                    len(metin),
                )
                return metin
            except Exception as e:
                log.exception("[WhisperSTT] openai kutuphanesi hatasi:")
                return f"[YAZIYA_CEVIR/Whisper] openai lib hatasi: {e}"

        except Exception as e:
            log.exception("[WhisperSTT] Whisper API hatasi:")
            import urllib.error as _ue

            if hasattr(e, "read"):
                try:
                    govde = e.read().decode(errors="replace")[:300]
                    return f"[YAZIYA_CEVIR/Whisper] HTTP hatasi: {govde}"
                except Exception as _e:
                    __import__("logging").getLogger(__name__).warning(
                        "[SessizExcept] %%s: %%s", type(_e).__name__, _e
                    )
            return f"[YAZIYA_CEVIR/Whisper] Hata: {e}"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Stub Voice Engine (local dummy / simÃ¼le)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class StubVoice(VoiceEngine):
    """Local dummy engine. API key gerekmez. Ses Ã¼retmez, simÃ¼le eder."""

    @property
    def ad(self) -> str:
        return "stub"

    def seslendir(self, text: str, voice: str = "alloy") -> str:
        return (
            f"[SESLENDIR/Stub] Simule edilen seslendirme.\n"
            f"  Metin: {text.strip()}\n"
            f"  Ses: {voice}\n"
            f"  (Stub engine: gercek ses icin OPENAI_API_KEY ayarlayin veya EdgeTTS kullanin)"
        )

    def yaziya_cevir(self, ses_dosyasi: str) -> str:
        return (
            f"[YAZIYA_CEVIR/Stub] Simule edilen metin cevrimi.\n"
            f"  Dosya: {ses_dosyasi}\n"
            f"  (Stub engine: gercek cevrim icin OPENAI_API_KEY ayarlayin)"
        )


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Voice Registry
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class VoiceRegistry:
    """Ses engine'lerini kaydet, seÃ§ ve Ã§alÄ±ÅŸtÄ±r.

    KullanÄ±m:
        vr = VoiceRegistry()
        vr.kaydet("openai", OpenAITTS())
        vr.kaydet("edge", EdgeTTS())
        engine = vr.sec("openai")
        engine.seslendir("Merhaba DÃ¼nya")
    """

    def __init__(self) -> None:
        self._engines: dict[str, VoiceEngine] = {}
        self._varsayilan: Optional[str] = None

    def kaydet(self, engine: VoiceEngine) -> None:
        """Bir engine kaydet."""
        adi = engine.ad
        self._engines[adi] = engine
        # VarsayÄ±lan: openai > whisper > edge > stub
        if self._varsayilan is None:
            self._varsayilan = adi
        elif adi == "openai" and engine.hazir:
            self._varsayilan = adi
        elif adi == "whisper" and engine.hazir and self._varsayilan not in ("openai",):
            self._varsayilan = adi
        elif (
            adi == "edge"
            and engine.hazir
            and self._varsayilan not in ("openai", "whisper")
        ):
            self._varsayilan = adi
        log.info(
            "[VoiceRegistry] Engine kaydedildi: %s (varsayilan: %s)",
            adi,
            self._varsayilan,
        )

    def sec(self, ad: str) -> Optional[VoiceEngine]:
        """Ada gÃ¶re engine seÃ§. Bulunamazsa varsayÄ±lanÄ± dÃ¶ndÃ¼r."""
        eng = self._engines.get(ad)
        if eng is None and self._varsayilan:
            log.warning(
                "[VoiceRegistry] '%s' bulunamadi, varsayilana dusuluyor: %s",
                ad,
                self._varsayilan,
            )
            return self._engines.get(self._varsayilan)
        return eng

    @property
    def varsayilan(self) -> Optional[VoiceEngine]:
        """VarsayÄ±lan engine'i dÃ¶ndÃ¼r."""
        return self._engines.get(self._varsayilan) if self._varsayilan else None

    def seslendir(self, engine_adi: str, text: str, voice: str = "alloy") -> str:
        """Bir engine ile metni sese Ã§evir."""
        if not text or not text.strip():
            return "[SESLENDIR] Hata: 'text' bos olamaz."
        eng = self.sec(engine_adi)
        if eng is None:
            return f"[SESLENDIR] '{engine_adi}' engine'i bulunamadi."
        if not eng.hazir:
            return f"[SESLENDIR] '{engine_adi}' hazir degil (API anahtari eksik)."
        try:
            return eng.seslendir(text.strip(), voice)
        except Exception as e:
            log.exception("[VoiceRegistry] '%s' seslendirme hatasi:", engine_adi)
            return f"[SESLENDIR] '{engine_adi}' hatasi: {e}"

    def yaziya_cevir(self, engine_adi: str, ses_dosyasi: str) -> str:
        """Bir engine ile ses dosyasÄ±nÄ± metne Ã§evir."""
        if not ses_dosyasi:
            return "[YAZIYA_CEVIR] Hata: 'ses_dosyasi' bos olamaz."
        eng = self.sec(engine_adi)
        if eng is None:
            return f"[YAZIYA_CEVIR] '{engine_adi}' engine'i bulunamadi."
        if not eng.hazir:
            return f"[YAZIYA_CEVIR] '{engine_adi}' hazir degil (API anahtari eksik)."
        try:
            return eng.yaziya_cevir(ses_dosyasi)
        except Exception as e:
            log.exception("[VoiceRegistry] '%s' yaziya_cevirme hatasi:", engine_adi)
            return f"[YAZIYA_CEVIR] '{engine_adi}' hatasi: {e}"


# â”€â”€ Global registry singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

_registry: Optional[VoiceRegistry] = None


def _get_registry() -> VoiceRegistry:
    """Global VoiceRegistry singleton'Ä±nÄ± oluÅŸtur/dÃ¶ndÃ¼r."""
    global _registry
    if _registry is None:
        _registry = VoiceRegistry()
        # Stub her zaman Ã§alÄ±ÅŸÄ±r
        _registry.kaydet(StubVoice())
        # OpenAI TTS
        try:
            _registry.kaydet(OpenAITTS())
        except Exception as e:
            log.warning("[VoiceRegistry] OpenAITTS yuklenemedi: %s", e)
        # OpenAI TTS HD
        try:
            _registry.kaydet(OpenAITTS(model="tts-1-hd"))
        except Exception as e:
            log.warning("[VoiceRegistry] OpenAITTS (hd) yuklenemedi: %s", e)
        # Edge TTS
        try:
            _registry.kaydet(EdgeTTS())
        except Exception as e:
            log.warning("[VoiceRegistry] EdgeTTS yuklenemedi: %s", e)
        # Whisper STT
        try:
            _registry.kaydet(WhisperSTT())
        except Exception as e:
            log.warning("[VoiceRegistry] WhisperSTT yuklenemedi: %s", e)
    return _registry


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tool FonksiyonlarÄ±
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def seslendir(text: str, voice: str = "alloy", backend: str = "") -> str:
    """SESLENDIR tool'u â€” metni sese Ã§evir.

    Args:
        text: Seslendirilecek metin.
        voice: Kullanilacak ses (openai: alloy/echo/fable/onyx/nova/shimmer,
               edge: tr-TR-AhmetNeural vb.).
        backend: Kullanilacak engine adi (openai, edge, stub).
                 Bos birakilirsa varsayilan kullanilir.

    Returns:
        Ses dosyasi yolu veya hata mesaji.
    """
    reg = _get_registry()
    engine_adi = backend.strip() if backend.strip() else ""
    if not engine_adi:
        eng = reg.varsayilan
        if eng is None:
            return "[SESLENDIR] Hata: hicbir engine kayitli degil."
        engine_adi = eng.ad
    return reg.seslendir(engine_adi, text, voice)


def yaziya_cevir(ses_dosyasi: str, backend: str = "whisper") -> str:
    """YAZIYA_CEVIR tool'u â€” ses dosyasÄ±nÄ± metne Ã§evir.

    Args:
        ses_dosyasi: Ses dosyasinin yolu.
        backend: Kullanilacak engine adi (whisper, stub).

    Returns:
        Cozulen metin veya hata mesaji.
    """
    reg = _get_registry()
    engine_adi = backend.strip() if backend.strip() else "whisper"
    return reg.yaziya_cevir(engine_adi, ses_dosyasi)


def voice_engine_listele() -> str:
    """Kayitli engine'leri listele."""
    reg = _get_registry()
    satirlar = ["[SESLENDIR] Kayitli engine'ler:"]
    for ad, eng in reg._engines.items():
        durum = "hazir" if eng.hazir else "API anahtari eksik"
        isaret = " >" if ad == reg._varsayilan else "  "
        satirlar.append(f"  {isaret} {ad} ({durum})")
    return "\n".join(satirlar)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Motor Kayit
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


def motor_kaydet(motor) -> None:
    """Motor tarafindan otomatik cagrilir. SESLENDIR ve YAZIYA_CEVIR tool'larini kaydeder."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    try:
        motor._plugin_arac_kaydet(
            "SESLENDIR",
            lambda ham="": _seslendir_ayristir_ve_calistir(ham),
            "Metni sese cevirir (coklu back-end).\n"
            ' Kullanim: SESLENDIR(text="...", voice="alloy", backend="openai|edge|stub")\n'
            "Varsayilan: OpenAI TTS > Edge TTS > stub\n"
            "OpenAI: OPENAI_API_KEY ortam degiskeni gerekli.\n"
            "  Sesler: alloy, echo, fable, onyx, nova, shimmer\n"
            "Edge: edge-tts pip paketi gerekli, internet baglantisi lazim.\n"
            "  Sesler: tr-TR-AhmetNeural, en-US-AriaNeural vb.\n"
            "Stub: API key gerekmez, simulasyon yapar.",
        )
        motor._plugin_arac_kaydet(
            "YAZIYA_CEVIR",
            lambda ham="": _yaziya_cevir_ayristir_ve_calistir(ham),
            "Ses dosyasini metne cevirir (Whisper STT).\n"
            ' Kullanim: YAZIYA_CEVIR(ses_dosyasi="...", backend="whisper|stub")\n'
            "Whisper: OPENAI_API_KEY ortam degiskeni gerekli.\n"
            "Stub: API key gerekmez, simulasyon yapar.",
        )
        motor._plugin_arac_kaydet(
            "SESLENDIR_BACKEND_LISTELE",
            lambda: voice_engine_listele(),
            "Kullanilabilir ses engine'lerini listeler.",
        )
    except Exception as e:
        log.warning("[VoiceEngine] Motor kayit hatasi: %s", e)


def _seslendir_ayristir_ve_calistir(ham: str) -> str:
    """SESLENDIR(ham) -> parametre ayristir."""
    import re as _re

    text = ""
    voice = "alloy"
    backend = ""

    t_match = _re.search(r'text\s*=\s*"([^"]*)"', ham)
    if t_match:
        text = t_match.group(1)

    v_match = _re.search(r'voice\s*=\s*"([^"]*)"', ham)
    if v_match:
        voice = v_match.group(1)

    bk_match = _re.search(r'backend\s*=\s*"([^"]*)"', ham)
    if bk_match:
        backend = bk_match.group(1)

    if not text:
        text = ham.strip().strip('"').strip("'")

    return seslendir(text, voice, backend)


def _yaziya_cevir_ayristir_ve_calistir(ham: str) -> str:
    """YAZIYA_CEVIR(ham) -> parametre ayristir."""
    import re as _re

    ses_dosyasi = ""
    backend = "whisper"

    s_match = _re.search(r'ses_dosyasi\s*=\s*"([^"]*)"', ham)
    if s_match:
        ses_dosyasi = s_match.group(1)

    bk_match = _re.search(r'backend\s*=\s*"([^"]*)"', ham)
    if bk_match:
        backend = bk_match.group(1)

    if not ses_dosyasi:
        ses_dosyasi = ham.strip().strip('"').strip("'")

    return yaziya_cevir(ses_dosyasi, backend)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Test
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

if __name__ == "__main__":
    print(voice_engine_listele())
    print("\n--- Stub Test ---")
    print(seslendir("Merhaba DÃ¼nya", backend="stub"))
    print("\n--- Stub STT Test ---")
    print(yaziya_cevir("test.mp3", backend="stub"))
