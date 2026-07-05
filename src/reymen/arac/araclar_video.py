# -*- coding: utf-8 -*-
"""
araclar_video.py â€” Video bilgi ve analiz araÃ§larÄ±.

  VIDEO_BILGI   â€” Video metadata (baÅŸlÄ±k, sÃ¼re, Ã§Ã¶zÃ¼nÃ¼rlÃ¼k, yÃ¼kleyen).
                  Uzak (YouTube vb.) iÃ§in yt-dlp, yerel dosya iÃ§in ffprobe kullanÄ±r.
  VIDEO_ANALIZ  â€” AltyazÄ± varsa onu, yoksa sesi Whisper ile metne Ã§evirir,
                  basit bir hÄ±zlÄ± Ã¶zet + transkript dÃ¶ner. AsÄ±l derin Ã¶zet
                  ReAct ajanÄ±nÄ±n kendi LLM'i tarafÄ±ndan bu metin Ã¼zerinden
                  yapÄ±lmasÄ± beklenir (araÃ§ burada ham/yarÄ±-iÅŸlenmiÅŸ veri saÄŸlar).

BaÄŸÄ±mlÄ±lÄ±klar (opsiyonel â€” eksikse araÃ§ aÃ§Ä±klayarak degrade eder):
    pip install yt-dlp                       # uzak video bilgisi + indirme
    pip install faster-whisper                # ses â†’ metin (Ã¶ncelikli)
    pip install openai-whisper                 # ses â†’ metin (fallback)
    ffmpeg / ffprobe sistemde kurulu olmalÄ±   # yerel video metadata + ses Ã§Ä±karma

MEDIA bu modÃ¼lde kullanÄ±lmaz (video dosyasÄ±nÄ±n kendisi gÃ¶nderilmiyor, sadece
metin/metadata dÃ¶ndÃ¼rÃ¼lÃ¼yor); biÃ§im diÄŸer araÃ§larla tutarlÄ± kalsÄ±n diye
ileride video MEDIA'sÄ± eklenmek istenirse aynÄ± sÃ¶zleÅŸme izlenebilir:

    [MEDIA type="video" src="<url-veya-yol>"]
"""

import glob
import logging
import os
import re
import subprocess
import tempfile
import threading

logger = logging.getLogger(__name__)

_whisper_lock = threading.Lock()
_fw_model = None
_ow_model = None


# â”€â”€ Whisper (baÄŸÄ±msÄ±z kopya â€” diÄŸer modÃ¼llere baÄŸÄ±mlÄ± olmamak iÃ§in) â”€â”€


def _faster_whisper_model(model_adi: str = "small"):
    global _fw_model
    if _fw_model is None:
        with _whisper_lock:
            if _fw_model is None:
                from faster_whisper import WhisperModel

                _fw_model = WhisperModel(model_adi, device="cpu", compute_type="int8")
    return _fw_model


def _openai_whisper_model(model_adi: str = "base"):
    global _ow_model
    if _ow_model is None:
        with _whisper_lock:
            if _ow_model is None:
                import whisper

                _ow_model = whisper.load_model(model_adi)
    return _ow_model


def _whisper_transcribe(dosya_yolu: str, dil: str = "tr") -> str:
    dil_param = dil.strip() if dil and dil.strip() else None
    try:
        model = _faster_whisper_model()
        segments, _bilgi = model.transcribe(dosya_yolu, language=dil_param)
        return " ".join(s.text.strip() for s in segments).strip()
    except ImportError:
        logger.warning("[fix_01_sessiz_except] ImportError")
    except Exception as e:
        logger.warning(
            "[VIDEO_ANALIZ] faster-whisper hatasÄ±, openai-whisper deneniyor: %s", e
        )
    try:
        model = _openai_whisper_model()
        sonuc = model.transcribe(dosya_yolu, language=dil_param)
        return (sonuc.get("text") or "").strip()
    except ImportError:
        return ""
    except Exception as e:
        logger.warning("[VIDEO_ANALIZ] openai-whisper hatasÄ±: %s", e)
        return ""


# â”€â”€ AltyazÄ± dosyasÄ± ayrÄ±ÅŸtÄ±rma (vtt/srt â†’ dÃ¼z metin) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _altyazi_dosya_oku(yol: str) -> str:
    with open(yol, encoding="utf-8", errors="replace") as f:
        ham = f.read()
    satirlar = []
    for satir in ham.splitlines():
        s = satir.strip()
        if not s or s.upper().startswith(("WEBVTT", "NOTE", "KIND:", "LANGUAGE:")):
            continue
        if re.match(r"^\d+$", s):  # srt sÄ±ra numarasÄ±
            continue
        if "-->" in s:  # zaman damgasÄ±
            continue
        s = re.sub(r"<[^>]+>", "", s)  # vtt etiketleri
        if s:
            satirlar.append(s)
    # otomatik altyazÄ±larda sÄ±k gÃ¶rÃ¼len ardÄ±ÅŸÄ±k tekrarlarÄ± sil
    temiz = []
    for s in satirlar:
        if not temiz or temiz[-1] != s:
            temiz.append(s)
    return " ".join(temiz)


def _basit_ozet(metin: str, n_cumle: int = 3, maks_uzunluk: int = 400) -> str:
    cumleler = re.split(r"(?<=[.!?])\s+", metin.strip())
    secim = " ".join(c for c in cumleler[:n_cumle] if c)
    if len(secim) > maks_uzunluk:
        secim = secim[:maks_uzunluk] + "â€¦"
    return secim or "(Ã¶zet Ã§Ä±karÄ±lamadÄ±)"


# â”€â”€ Uzak video (YouTube vb.) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _video_bilgi_uzak(url: str) -> str:
    try:
        import yt_dlp
    except ImportError:
        return "[VIDEO_BILGI] Hata: yt-dlp kurulu deÄŸil (pip install yt-dlp)."
    try:
        with yt_dlp.YoutubeDL(
            {"quiet": True, "no_warnings": True, "skip_download": True}
        ) as ydl:
            info = ydl.extract_info(url, download=False)
        baslik = info.get("title", "?")
        sure = info.get("duration", "?")
        genislik, yukseklik = info.get("width", "?"), info.get("height", "?")
        yukleyen = info.get("uploader", "?")
        return (
            f"[VIDEO_BILGI]\nBaÅŸlÄ±k: {baslik}\nSÃ¼re: {sure}s\n"
            f"Ã‡Ã¶zÃ¼nÃ¼rlÃ¼k: {genislik}x{yukseklik}\nYÃ¼kleyen: {yukleyen}\nURL: {url}"
        )
    except Exception as e:
        return f"[VIDEO_BILGI] Hata: {e}"


def _altyazi_veya_ses_metni_uzak(url: str, dil: str) -> tuple:
    """Ã–nce altyazÄ± indirmeyi dener; yoksa sesi indirip Whisper ile Ã§evirir."""
    import yt_dlp

    with tempfile.TemporaryDirectory() as tmp:
        # 1) AltyazÄ± dene (manuel + otomatik)
        try:
            with yt_dlp.YoutubeDL(
                {
                    "quiet": True,
                    "no_warnings": True,
                    "skip_download": True,
                    "writesubtitles": True,
                    "writeautomaticsub": True,
                    "subtitleslangs": [dil or "tr", "en"],
                    "outtmpl": os.path.join(tmp, "%(id)s.%(ext)s"),
                }
            ) as ydl:
                ydl.download([url])
        except Exception as e:
            logger.warning("[VIDEO_ANALIZ] altyazÄ± indirme hatasÄ±: %s", e)

        altyazilar = glob.glob(os.path.join(tmp, "*.vtt")) + glob.glob(
            os.path.join(tmp, "*.srt")
        )
        if altyazilar:
            return _altyazi_dosya_oku(altyazilar[0]), "altyazÄ±"

        # 2) Ses indir + Whisper
        try:
            with yt_dlp.YoutubeDL(
                {
                    "quiet": True,
                    "no_warnings": True,
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(tmp, "ses.%(ext)s"),
                }
            ) as ydl:
                ydl.download([url])
        except Exception as e:
            return "", f"ses_indirme_hatasi:{e}"

        ses_dosyalari = glob.glob(os.path.join(tmp, "ses.*"))
        if not ses_dosyalari:
            return "", "ses_bulunamadi"
        return _whisper_transcribe(ses_dosyalari[0], dil), "whisper(ses)"


# â”€â”€ Yerel video â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _video_bilgi_yerel(yol: str) -> str:
    if not os.path.exists(yol):
        return f"[VIDEO_BILGI] Hata: dosya bulunamadÄ±: {yol}"
    try:
        cikti = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                yol,
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        import json as _json

        veri = _json.loads(cikti.stdout)
        video_akisi = next(
            (s for s in veri.get("streams", []) if s.get("codec_type") == "video"), {}
        )
        sure = veri.get("format", {}).get("duration", "?")
        return (
            f"[VIDEO_BILGI]\nDosya: {yol}\nSÃ¼re: {sure}s\n"
            f"Ã‡Ã¶zÃ¼nÃ¼rlÃ¼k: {video_akisi.get('width', '?')}x{video_akisi.get('height', '?')}\n"
            f"Codec: {video_akisi.get('codec_name', '?')}"
        )
    except FileNotFoundError:
        boyut_mb = os.path.getsize(yol) / 1_048_576
        return (
            f"[VIDEO_BILGI] (ffprobe kurulu deÄŸil, sÄ±nÄ±rlÄ± bilgi)\n"
            f"Dosya: {yol}\nBoyut: {boyut_mb:.1f} MB"
        )
    except Exception as e:
        return f"[VIDEO_BILGI] Hata: {e}"


def _yerel_video_ses_metni(yol: str, dil: str) -> tuple:
    with tempfile.TemporaryDirectory() as tmp:
        ses_yolu = os.path.join(tmp, "ses.wav")
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    yol,
                    "-vn",
                    "-ac",
                    "1",
                    "-ar",
                    "16000",
                    ses_yolu,
                ],
                capture_output=True,
                timeout=180,
                check=True,
            )
        except FileNotFoundError:
            return "", "ffmpeg_kurulu_degil"
        except subprocess.CalledProcessError as e:
            return "", f"ffmpeg_hatasi:{e}"
        return _whisper_transcribe(ses_yolu, dil), "whisper(yerel)"


# â”€â”€ Ana araÃ§lar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def video_bilgi(kaynak: str) -> str:
    """Video metadata dÃ¶ner (baÅŸlÄ±k, sÃ¼re, Ã§Ã¶zÃ¼nÃ¼rlÃ¼k). URL veya yerel dosya yolu kabul eder."""
    if not kaynak or not kaynak.strip():
        return "[VIDEO_BILGI] Hata: kaynak boÅŸ olamaz."
    kaynak = kaynak.strip()
    if kaynak.startswith(("http://", "https://")):
        return _video_bilgi_uzak(kaynak)
    return _video_bilgi_yerel(kaynak)


def video_analiz(kaynak: str, dil: str = "tr", max_karakter: str = "4000") -> str:
    """Videodan (altyazÄ± veya Whisper ile) metin Ã§Ä±karÄ±r, hÄ±zlÄ± Ã¶zet + transkript dÃ¶ner."""
    if not kaynak or not kaynak.strip():
        return "[VIDEO_ANALIZ] Hata: kaynak boÅŸ olamaz."
    kaynak = kaynak.strip()
    try:
        maks = int(max_karakter)
    except (TypeError, ValueError):
        maks = 4000

    try:
        if kaynak.startswith(("http://", "https://")):
            metin, kaynak_tip = _altyazi_veya_ses_metni_uzak(kaynak, dil)
        else:
            if not os.path.exists(kaynak):
                return f"[VIDEO_ANALIZ] Hata: dosya bulunamadÄ±: {kaynak}"
            metin, kaynak_tip = _yerel_video_ses_metni(kaynak, dil)
    except ImportError as e:
        return f"[VIDEO_ANALIZ] Hata: gerekli kÃ¼tÃ¼phane kurulu deÄŸil ({e})."
    except Exception as e:
        logger.error("[VIDEO_ANALIZ] hata: %s", e)
        return f"[VIDEO_ANALIZ] Hata: {e}"

    if not metin or not metin.strip():
        return (
            f"[VIDEO_ANALIZ] Hata: metin Ã§Ä±karÄ±lamadÄ± (kaynak_tip={kaynak_tip}). "
            "AltyazÄ± yok ve Whisper baÅŸarÄ±sÄ±z olmuÅŸ olabilir (ffmpeg/yt-dlp/whisper kontrol edin)."
        )

    metin = metin.strip()
    hizli_ozet = _basit_ozet(metin)
    kisaltilmis = metin[:maks] + ("â€¦" if len(metin) > maks else "")
    return (
        f"[VIDEO_ANALIZ] (kaynak: {kaynak_tip})\n"
        f"HÄ±zlÄ± Ã¶zet: {hizli_ozet}\n\n"
        f"Transkript/AltyazÄ± ({len(metin)} karakter, {len(kisaltilmis)} gÃ¶steriliyor):\n{kisaltilmis}"
    )


# â”€â”€ Motor kayÄ±t â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_kaydet(motor) -> None:
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    try:
        motor._plugin_arac_kaydet(
            "VIDEO_BILGI",
            video_bilgi,
            "Video metadata (baÅŸlÄ±k, sÃ¼re, Ã§Ã¶zÃ¼nÃ¼rlÃ¼k) dÃ¶ner. Parametreler: kaynak (url/yol).",
        )
        motor._plugin_arac_kaydet(
            "VIDEO_ANALIZ",
            video_analiz,
            "YouTube/yerel videodan altyazÄ± veya Whisper ile metin Ã§Ä±karÄ±r, hÄ±zlÄ± Ã¶zet "
            "+ transkript dÃ¶ner. Parametreler: kaynak (url/yol), dil, max_karakter.",
        )
    except Exception as e:
        print(f"[AraclarVideo] Motor kayÄ±t hatasÄ±: {e}")


if __name__ == "__main__":
    print("araclar_video hazÄ±r.")
