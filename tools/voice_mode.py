# -*- coding: utf-8 -*-
"""voice_mode.py — Ses Modu Yonetim Araci.

ReYMeN icin Windows SAPI (Speech API) uzerinden metin okuma
ve mikrofon dinleme islevlerini saglar.
"""

import time
from pathlib import Path


def sesli_oku(metin: str, ses: str = "default") -> str:
    """Belirtilen metni Windows SAPI ile sesli okur.

    Args:
        metin: Okunacak metin (zorunlu)
        ses: Kullanilacak ses (varsayilan: "default", alternatif: "male", "female")

    Returns:
        str: Durum mesaji
    """
    if not metin:
        return "[Ses]: Okunacak metin gerekli."

    try:
        import win32com.client
        konusma = win32com.client.Dispatch("SAPI.SpVoice")

        # Ses secimi
        sesler = konusma.GetVoices()
        if ses == "male" and sesler.Count > 1:
            konusma.Voice = sesler.Item(1)
        elif ses == "female" and sesler.Count > 0:
            konusma.Voice = sesler.Item(0)
        # "default" icin ilk ses kullanilir

        konusma.Speak(metin)
        return f"[Ses]: Metin okundu ({len(metin)} karakter, ses: {ses})."

    except ImportError:
        # win32com yoksa fallback
        try:
            import subprocess
            # PowerShell TTS fallback
            ps_script = f"""
            Add-Type -AssemblyName System.Speech;
            $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
            $synth.Speak('{metin.replace("'", "''")}');
            """
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, timeout=30
            )
            return f"[Ses]: Metin okundu (PowerShell TTS, {len(metin)} karakter)."
        except Exception as e2:
            return f"[Ses]: TTS kullanilamiyor - {e2}"

    except Exception as e:
        return f"[Ses]: Windows SAPI hatasi - {e}"


def mikrofon_dinle(sure: int = 5) -> str:
    """Mikrofondan ses kaydi alir ve metne cevirir.

    Args:
        sure: Dinleme suresi (saniye, varsayilan: 5)

    Returns:
        str: Alinan metin veya hata mesaji
    """
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()

        with sr.Microphone() as kaynak:
            recognizer.adjust_for_ambient_noise(kaynak)
            ses = recognizer.listen(kaynak, timeout=sure, phrase_time_limit=sure)

        try:
            metin = recognizer.recognize_google(ses, language="tr-TR")
            return f"[Ses]: Alinan metin: {metin}"
        except sr.UnknownValueError:
            return "[Ses]: Ses anlasilamadi."
        except sr.RequestError as e:
            return f"[Ses]: Tanima servisi hatasi - {e}"

    except ImportError:
        return "[Ses]: 'speech_recognition' kutuphanesi gerekli (pip install SpeechRecognition)."
    except OSError as e:
        return f"[Ses]: Mikrofon erisim hatasi - {e}"
    except Exception as e:
        return f"[Ses]: Mikrofon dinleme hatasi - {e}"


def run(**kwargs) -> str:
    """Ses modu yonlendirme fonksiyonu.

    Args:
        islem (str): Yapilacak islem - "sesli_oku" veya "mikrofon_dinle" (zorunlu)
        metin (str): Okunacak metin (sesli_oku icin)
        ses (str): Ses tipi (sesli_oku icin, varsayilan: "default")
        sure (int): Dinleme suresi (mikrofon_dinle icin, varsayilan: 5)

    Returns:
        str: Islem sonucu
    """
    islem = kwargs.get("islem", "")
    if not islem:
        return "[Ses]: 'islem' parametresi zorunlu (sesli_oku, mikrofon_dinle)."

    try:
        if islem == "sesli_oku":
            return sesli_oku(
                kwargs.get("metin", ""),
                kwargs.get("ses", "default")
            )
        elif islem == "mikrofon_dinle":
            return mikrofon_dinle(kwargs.get("sure", 5))
        else:
            return f"[Ses]: Bilinmeyen islem: {islem}"
    except Exception as e:
        return f"[Ses]: Hata - {e}"


def ping() -> bool:
    return True


if __name__ == "__main__":
    print(run(islem="sesli_oku", metin="Merhaba, ben ReYMeN."))
