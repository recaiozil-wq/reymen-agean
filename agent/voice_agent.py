#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent/voice_agent.py — ReYMeN Ses Modu Yoneticisi.

Tum ses islemlerini tek bir noktada toplar:
- TTS (Text-to-Speech): edge-tts, Windows SAPI (arka arkada dener)
- STT (Speech-to-Text): speech_recognition ile mikrofon
- /voice slash komutu
- Config entegrasyonu
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("reymen.voice")

# ── Kullanilabilir Backend'ler ────────────────────────────────────

def _edge_tts_var_mi() -> bool:
    """edge-tts CLI kurulu mu?"""
    try:
        subprocess.run(
            ["edge-tts", "--help"],
            capture_output=True, timeout=5,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return False

def _sapi_var_mi() -> bool:
    """Windows SAPI (win32com) kurulu mu?"""
    try:
        import win32com.client  # noqa
        return True
    except ImportError:
        return False

def _speech_rec_var_mi() -> bool:
    """speech_recognition kurulu mu?"""
    try:
        import speech_recognition  # noqa
        return True
    except ImportError:
        return False

def _faster_whisper_var_mi() -> bool:
    """faster-whisper (yerel STT) kurulu mu?"""
    try:
        from faster_whisper import WhisperModel  # noqa
        return True
    except ImportError:
        return False


# ── TTS Backend'leri ──────────────────────────────────────────────

def _tts_edge(metin: str, ses: str = "tr-TR-AhmetNeural") -> Optional[str]:
    """Edge-TTS ile metni sese cevir, mp3 yolunu don."""
    fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    try:
        subprocess.run(
            ["edge-tts", "--voice", ses, "--text", metin.strip(),
             "--write-media", tmp_path],
            check=True, capture_output=True, timeout=30,
        )
        return tmp_path
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        return None

def _tts_sapi(metin: str, ses: str = "default") -> Optional[str]:
    """Windows SAPI ile konus (dosya yok, direkt ses cikisi)."""
    try:
        import win32com.client
        konusma = win32com.client.Dispatch("SAPI.SpVoice")
        sesler = konusma.GetVoices()
        if ses == "male" and sesler.Count > 1:
            konusma.Voice = sesler.Item(1)
        elif ses == "female" and sesler.Count > 0:
            konusma.Voice = sesler.Item(0)
        konusma.Speak(metin)
        return "[SAPI]"
    except ImportError:
        try:
            ps_script = (
                "Add-Type -AssemblyName System.Speech; "
                "$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                "$synth.Speak('%s');" % metin.replace("'", "''")
            )
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, timeout=30,
            )
            return "[PowerShell]"
        except Exception as e:
            logger.warning(f"SAPI TTS hatasi: {e}")
            return None

def _tts_powershell(metin: str) -> Optional[str]:
    """PowerShell System.Speech ile TTS (dosya yok)."""
    try:
        ps = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            "$s.Speak('%s')" % metin.replace("'", "''")
        )
        subprocess.run(
            ["powershell", "-Command", ps],
            capture_output=True, timeout=30,
        )
        return "[PowerShell]"
    except Exception:
        return None


# ── STT Backend ───────────────────────────────────────────────────

def _stt_speech_rec(sure: int = 5) -> Optional[str]:
    """Mikrofondan ses al, metne cevir."""
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        with sr.Microphone() as kaynak:
            r.adjust_for_ambient_noise(kaynak)
            ses = r.listen(kaynak, timeout=sure, phrase_time_limit=sure)
        return r.recognize_google(ses, language="tr-TR")
    except ImportError:
        return None
    except LookupError:
        return None
    except Exception as e:
        logger.debug(f"STT hatasi: {e}")
        return None

def _stt_faster_whisper(sure: int = 5) -> Optional[str]:
    """Mikrofondan ses al, faster-whisper ile yerel STT yap.

    API key gerekmez, model lokal calisir (CPU'da int8 quantized).
    Gereken: pip install faster-whisper sounddevice soundfile

    Args:
        sure: Maksimum kayit suresi (saniye).

    Returns:
        str: Taninan metin veya None.
    """
    try:
        from faster_whisper import WhisperModel

        # Ses kaydi icin sounddevice
        import sounddevice as sd
        import soundfile as sf

        import numpy as np
        import tempfile

        sample_rate = 16000
        kanal = 1  # mono

        logger.info(f"faster-whisper: {sure} saniye dinleniyor...")
        kayit = sd.rec(
            int(sure * sample_rate),
            samplerate=sample_rate,
            channels=kanal,
            dtype="int16",
        )
        sd.wait()

        # Gecici WAV dosyasina yaz
        fd, tmp_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        sf.write(tmp_path, kayit, sample_rate)

        # Transkripsiyon (base model, CPU, int8)
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(tmp_path, language="tr")
        metin = " ".join(seg.text for seg in segments).strip()

        # Temizlik
        Path(tmp_path).unlink(missing_ok=True)

        return metin if metin else None

    except ImportError:
        logger.warning(
            "faster-whisper/local STT kurulu degil. "
            "Kurulum: pip install faster-whisper sounddevice soundfile"
        )
        return None
    except Exception as e:
        logger.debug(f"faster-whisper STT hatasi: {e}")
        return None


# ── VoiceMode Yoneticisi ──────────────────────────────────────────

class VoiceMode:
    """ReYMeN ses modu yoneticisi.

    Kullanilabilir backend'leri otomatik tespit eder,
    TTS ve STT islemlerini yapar.
    """

    def __init__(self, config: Optional[dict] = None):
        self._config = config or {}

        # Backend tespiti
        voice_cfg = (self._config.get("voice") or {})
        self._varsayilan_ses = voice_cfg.get("default_voice", "tr-TR-AhmetNeural")
        self._varsayilan_sure = voice_cfg.get("listen_seconds", 5)
        self._arka_tts = voice_cfg.get("fallback_tts", True)

        self.edge_tts = _edge_tts_var_mi()
        self.sapi = _sapi_var_mi()
        self.speech_rec = _speech_rec_var_mi()
        self.faster_whisper = _faster_whisper_var_mi()
        self.powershell = True  # Windows'ta her zaman var

        logger.info(
            f"Voice: edge-tts={self.edge_tts}, "
            f"SAPI={self.sapi}, "
            f"SpeechRec={self.speech_rec}, "
            f"faster-whisper={self.faster_whisper}"
        )

    # ── TTS ───────────────────────────────────────────────────────

    def konus(self, metin: str, ses: Optional[str] = None) -> str:
        """Metni sesli okur.

        Oncelik: edge-tts (dosyaya yazar) -> SAPI -> PowerShell
        """
        if not metin or not metin.strip():
            return "[Hata]: Metin gerekli."

        ses = ses or self._varsayilan_ses
        metin = metin.strip()

        # 1) edge-tts (en kaliteli)
        if self.edge_tts:
            dosya = _tts_edge(metin, ses)
            if dosya:
                return f"[Ses] edge-tts: {metin[:50]}... -> {dosya}"

        # 2) SAPI (Windows)
        if self.sapi:
            sonuc = _tts_sapi(metin, ses)
            if sonuc:
                return f"[Ses] SAPI: {metin[:50]}..."

        # 3) PowerShell (fallback)
        if self._arka_tts:
            sonuc = _tts_powershell(metin)
            if sonuc:
                return f"[Ses] PowerShell: {metin[:50]}..."

        return f"[Hata]: Kullanilabilir TTS backend'i yok."

    def konus_dosyaya(self, metin: str, ses: Optional[str] = None) -> Optional[str]:
        """Metni sese cevir, dosya yolunu don.
        Sadece edge-tts ile calisir.
        """
        if not self.edge_tts:
            return None
        return _tts_edge(metin.strip(), ses or self._varsayilan_ses)

    # ── STT ───────────────────────────────────────────────────────

    def dinle(self, sure: Optional[int] = None) -> str:
        """Mikrofondan ses al, metne cevir.

        faster-whisper kuruluysa yerel STT kullanir,
        degilse speech_recognition + Google API.
        """
        sure = sure or self._varsayilan_sure
        if self.faster_whisper:
            metin = _stt_faster_whisper(sure)
            if metin:
                return f"[Ses] Alinan metin: {metin}"
            return "[Ses] Ses anlasilamadi veya zaman asimi."
        if not self.speech_rec:
            return "[Hata]: speech_recognition kutuphanesi gerekli (pip install SpeechRecognition)"

        metin = _stt_speech_rec(sure)
        if metin:
            return f"[Ses] Alinan metin: {metin}"
        return "[Ses] Ses anlasilamadi veya zaman asimi."

    # ── /voice Slash Komutu ──────────────────────────────────────

    def komut_islem(self, args: str = "") -> str:
        """/voice komutunu isle.

        argumanlar:
          bos / status / durum -> Mevcut durum
          konus <metin>        -> Sesli okur
          dinle [sure]         -> Mikrofon dinler
          ses <ad>             -> Varsayilan sesi degistir
        """
        if not args or args.lower() in ("status", "durum", ""):
            return self._durum_goster()

        parts = args.strip().split(maxsplit=1)
        alt_komut = parts[0].lower()
        alt_args = parts[1] if len(parts) > 1 else ""

        if alt_komut == "konus":
            if not alt_args:
                return "[Voice] Kullanım: /voice konus <metin>"
            return self.konus(alt_args)

        if alt_komut == "dinle":
            sure = 5
            if alt_args:
                try:
                    sure = int(alt_args)
                except ValueError:
                    logger.warning("[fix_01_sessiz_except] ValueError")
            return self.dinle(sure)

        if alt_komut == "ses":
            if alt_args:
                self._varsayilan_ses = alt_args
                return f"[Voice] Varsayilan ses degistirildi: {alt_args}"
            return f"[Voice] Gecerli ses: {self._varsayilan_ses}"

        if alt_komut == "test":
            return self.konus("Test ses calismasi. ReYMeN ses modu aktif.")

        return f"[Voice] Bilinmeyen komut: {alt_komut}. Kullanım: /voice [konus|dinle|ses|test|status]"

    # ── Durum ─────────────────────────────────────────────────────

    def _durum_goster(self) -> str:
        lines = [
            "ReYMeN Ses Modu",
            f"  Varsayilan ses: {self._varsayilan_ses}",
            f"  edge-tts:      {'✅' if self.edge_tts else '❌'}",
            f"  SAPI:          {'✅' if self.sapi else '❌'}",
            f"  STT (Google):  {'✅' if self.speech_rec else '❌'}",
            f"  STT (Yerel):   {'✅' if self.faster_whisper else '❌'}",
            "",
            "Komutlar:",
            "  /voice               -> Bu durum",
            "  /voice konus <metin>  -> Sesli oku",
            "  /voice dinle [sure]   -> Mikrofon dinle",
            "  /voice ses <ad>       -> Ses degistir",
            "  /voice test           -> Test sesi",
        ]
        return "\n".join(lines)

    # ── Ping ──────────────────────────────────────────────────────

    def ping(self) -> bool:
        return True

    # ── Streaming TTS ──────────────────────────────────────────────

    @staticmethod
    def _cumle_bol(metin: str) -> list:
        """Metni cümlelere böl (akışlı TTS için).

        Türkçe cümle sonu karakterleri: . ! ? … : ;
        """
        import re
        # Cümle sonu patterni
        pattern = r'[^.!?…:;]+[.!?…:;]+'
        cumleler = re.findall(pattern, metin)
        # Kalan metin varsa ekle
        kalan = re.sub(pattern, '', metin).strip()
        if kalan:
            cumleler.append(kalan)
        # Çok kısa cümleleri birleştir (min 20 karakter)
        sonuc = []
        tampon = ""
        for c in cumleler:
            tampon += " " + c.strip()
            if len(tampon) >= 20:
                sonuc.append(tampon.strip())
                tampon = ""
        if tampon.strip():
            sonuc.append(tampon.strip())
        return sonuc or [metin]

    def konus_stream(self, metin: str, ses: Optional[str] = None) -> str:
        """Metni cümle cümle seslendir (akışlı TTS).

        Uzun metinleri cümlelere böler, her cümleyi ayrı ayrı
        edge-tts'e gönderir. Telegram/Discord için ses dosyası
        olarak birleştirilmiş son dosyayı döndürür.

        Returns:
            str: Oluşturulan ses dosyasının yolu
        """
        import tempfile

        if not metin or not metin.strip():
            return "[Hata]: Metin gerekli."

        ses = ses or self._varsayilan_ses
        metin = metin.strip()

        # Cümlelere böl
        cumleler = self._cumle_bol(metin)

        if not cumleler:
            return "[Hata]: Cümle bulunamadı."

        # Markdown temizle
        import re
        temiz = []
        for c in cumleler:
            c = re.sub(r'<[^>]+>', '', c)  # HTML tag kaldır
            c = re.sub(r'\*\*|__|~~|`|```', '', c)  # Markdown kaldır
            c = c.strip()
            if c:
                temiz.append(c)

        if not temiz:
            return "[Hata]: Temizlenmiş cümle yok."

        if len(temiz) == 1:
            # Tek cümle -> normal konus
            return self.konus(temiz[0], ses)

        # Çok cümle -> her birini ayrı oynat (tek dosyada birleştirme yok)
        son_dosya = None
        for i, cumle in enumerate(temiz):
            if self.edge_tts:
                dosya = _tts_edge(cumle, ses)
                if dosya:
                    son_dosya = dosya
            elif self.sapi:
                _tts_sapi(cumle, ses)
            else:
                _tts_powershell(cumle)

        if son_dosya:
            # Bilgi: kaç cümle işlendi
            cikti = (
                f"[Ses] Akışlı TTS: {len(temiz)} cümle -> {son_dosya}\n"
                f"  İlk cümle: {temiz[0][:60]}..."
            )
            return cikti

        return "[Ses] Akışlı TTS: tüm cümleler seslendirildi."

    # ── Akıllı Dinleme (Sessizlik Algılama) ────────────────────────

    def dinle_akilli(self, max_sure: int = 15, sessizlik_esik: int = 3) -> str:
        """Mikrofonu aç, konuşma bitene kadar bekle (sessizlik algılama).

        faster-whisper kuruluysa onu (yerel, API'siz) kullanir,
        degilse speech_recognition (Google API) ile devam eder.

        Args:
            max_sure: Maksimum dinleme süresi (saniye)
            sessizlik_esik: Sessizlik algılama eşiği (saniye)

        Returns:
            str: Alınan metin
        """
        # 1) faster-whisper (yerel, API gerekmez)
        if self.faster_whisper:
            metin = _stt_faster_whisper(sure=max_sure)
            if metin:
                return metin
            # Bos metin -> sessizlik, bos don
            return ""

        # 2) speech_recognition (Google API)
        if not self.speech_rec:
            return "[Hata]: speech_recognition gerekli."

        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.Microphone() as kaynak:
                r.adjust_for_ambient_noise(kaynak, duration=0.5)
                # phrase_time_limit ile sessizlik algılama
                ses = r.listen(
                    kaynak,
                    timeout=max_sure,
                    phrase_time_limit=max_sure,
                )
            metin = r.recognize_google(ses, language="tr-TR")
            if metin:
                return metin
            return ""
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except ImportError:
            return "[Hata]: speech_recognition kutuphanesi gerekli."
        except Exception as e:
            logger.debug(f"Akilli dinleme hatasi: {e}")
            return ""

    # ── Etkileşimli Döngü (Dinle -> İşle -> Konuş) ─────────────────

    def dongu(self, tur_sayisi: int = 3) -> str:
        """Etkileşimli ses döngüsü: dinle -> işle (simüle) -> konuş.

        Not: Gerçek AI işleme motor entegrasyonu gerektirir.
        Bu versiyonda sadece ses giriş/çıkış döngüsünü test eder.

        Args:
            tur_sayisi: Kaç tur çalışacağı (varsayılan: 3)

        Returns:
            str: Döngü raporu
        """
        satirlar = [f"🎙️ Ses döngüsü başladı ({tur_sayisi} tur)"] if tur_sayisi else ["🎙️ Ses döngüsü başladı (sınırsız)"]

        if self.edge_tts:
            _tts_edge("Ses dongusu basladi. Konusmaya baslayin.", self._varsayilan_ses)

        tur = 0
        while tur_sayisi is None or tur < tur_sayisi:
            tur += 1

            # Dinle
            satirlar.append(f"\n  Tur {tur}: dinleniyor...")
            metin = self.dinle_akilli(max_sure=10, sessizlik_esik=2)

            if not metin:
                satirlar.append("    ⏭️  Ses algılanmadı, geçiliyor.")
                continue

            if metin.startswith("[Hata]"):
                satirlar.append(f"    ❌ {metin}")
                break

            satirlar.append(f"    🎤 Alınan: {metin[:80]}")

            # Dur/kapat kontrolü
            dur_kelimeleri = ["kapat", "dur", "çık", "yeter", "dur dur"]
            if any(k in metin.lower() for k in dur_kelimeleri):
                satirlar.append("    ⏹️  Dur komutu algılandı, döngü sonlanıyor.")
                break

            # Konuş (yankı)
            yanit = f"{metin} dediniz."
            self.konus(yanit)
            satirlar.append(f"    🔄 Yanıt: {yanit[:60]}...")

        satirlar.append(f"\n✅ Ses döngüsü tamamlandı ({tur} tur).")
        return "\n".join(satirlar)

    # ── Genişletilmiş Komut İşleme ─────────────────────────────────

    def komut_islem(self, args: str = "") -> str:
        """/voice komutunu isle.

        argumanlar:
          bos / status / durum -> Mevcut durum
          konus <metin>        -> Sesli okur
          dinle [sure]         -> Mikrofon dinler
          ses <ad>             -> Varsayilan sesi degistir
          stream <metin>       -> Akışlı TTS (cümle cümle)
          dongu [tur]          -> Etkileşimli döngü
          test                 -> Test sesi
        """
        if not args or args.lower() in ("status", "durum", ""):
            return self._durum_goster()

        parts = args.strip().split(maxsplit=1)
        alt_komut = parts[0].lower()
        alt_args = parts[1] if len(parts) > 1 else ""

        if alt_komut == "konus":
            if not alt_args:
                return "[Voice] Kullanım: /voice konus <metin>"
            return self.konus(alt_args)

        if alt_komut == "dinle":
            sure = 5
            if alt_args:
                try:
                    sure = int(alt_args)
                except ValueError:
                    logger.warning("[fix_01_sessiz_except] ValueError")
            return self.dinle(sure)

        if alt_komut == "ses":
            if alt_args:
                self._varsayilan_ses = alt_args
                return f"[Voice] Varsayilan ses degistirildi: {alt_args}"
            return f"[Voice] Gecerli ses: {self._varsayilan_ses}"

        if alt_komut == "stream":
            if not alt_args:
                return "[Voice] Kullanım: /voice stream <uzun metin>"
            return self.konus_stream(alt_args)

        if alt_komut == "dongu":
            tur_sayisi = 3
            if alt_args:
                try:
                    tur_sayisi = int(alt_args)
                except ValueError:
                    logger.warning("[fix_01_sessiz_except] ValueError")
            return self.dongu(tur_sayisi)

        if alt_komut == "test":
            return self.konus("Test ses calismasi. ReYMeN ses modu aktif.")

        return (
            f"[Voice] Bilinmeyen komut: {alt_komut}. "
            f"Kullanım: /voice [konus|dinle|ses|stream|dongu|test|status]"
        )


# ── Singleton ─────────────────────────────────────────────────────

_voice_instance: Optional[VoiceMode] = None


def voice_mode(config: Optional[dict] = None) -> VoiceMode:
    global _voice_instance
    if _voice_instance is None:
        _voice_instance = VoiceMode(config)
    return _voice_instance
