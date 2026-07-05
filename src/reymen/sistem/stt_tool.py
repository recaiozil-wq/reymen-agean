# -*- coding: utf-8 -*-
"""
STT Tool â€” Sesi metne cevirir (faster-whisper).
ReYMeN icin native STT araci.

Kullanim:
    from reymen.sistem.stt_tool import sesi_metne_cevir
    metin = sesi_metne_cevir("ses.mp3")
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# faster-whisper
_WHISPER_MODEL = None
VARSAYILAN_MODEL = "tiny"  # hafif, hizli
VARSAYILAN_DIL = "tr"

PROJE_KOKU = Path(__file__).resolve().parent.parent.parent


def _model_yukle(model_boyut: str = VARSAYILAN_MODEL) -> Any:
    """faster-whisper modelini yukle (singleton)."""
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        try:
            from faster_whisper import WhisperModel

            _WHISPER_MODEL = WhisperModel(
                model_boyut,
                device="cpu",
                compute_type="int8",
                cpu_threads=4,
                num_workers=2,
            )
            logger.info("[STT] Model yuklendi: %s (device=cpu, int8)", model_boyut)
        except Exception as e:
            logger.exception("[STT] Model yukleme hatasi: %s", e)
            raise
    return _WHISPER_MODEL


def sesi_metne_cevir(
    ses_yolu: str,
    dil: str = VARSAYILAN_DIL,
    model_boyut: str = VARSAYILAN_MODEL,
) -> str:
    """Ses dosyasini metne cevir.

    Parametreler:
        ses_yolu (str, zorunlu) â€” Ses dosyasi yolu (.mp3, .wav, .ogg).
        dil (str, opsiyonel) â€” Dil kodu (varsayilan: 'tr').
        model_boyut (str, opsiyonel) â€” Model boyutu (varsayilan: 'tiny').

    Doner:
        Transkripsiyon metni veya hata mesaji.
    """
    ses = Path(ses_yolu)
    if not ses.exists():
        return f"[HATA] Dosya bulunamadi: {ses_yolu}"
    if ses.stat().st_size == 0:
        return "[HATA] Dosya bos."

    try:
        model = _model_yukle(model_boyut)
        logger.info("[STT] Transkripsiyon basliyor: %s (dil=%s)", ses_yolu, dil)

        segmentler, bilgi = model.transcribe(
            str(ses),
            language=dil,
            beam_size=3,
            vad_filter=True,  # sessiz bolumleri atla
            vad_parameters=dict(
                min_silence_duration_ms=500,
                threshold=0.5,
            ),
        )

        metin_parcalari = []
        for segment in segmentler:
            metin_parcalari.append(segment.text)

        tam_metin = " ".join(metin_parcalari).strip()
        if not tam_metin:
            return "[UYARI] Ses taninamadi (bos transkripsiyon)."

        logger.info(
            "[STT] Transkripsiyon tamam: %d karakter, dil=%s",
            len(tam_metin),
            bilä¿¡æ¯.language if hasattr(bilgi, "language") else dil,
        )
        return tam_metin

    except ImportError:
        return "[HATA] faster-whisper kurulu degil. 'pip install faster-whisper' ile kurun."
    except Exception as e:
        logger.exception("[STT] Transkripsiyon hatasi: %s", e)
        return f"[HATA] {type(e).__name__}: {e}"


def stt_durum() -> str:
    """STT sistem durumu."""
    try:
        import faster_whisper

        fw_version = getattr(faster_whisper, "__version__", "?")
    except ImportError:
        return "âŒ faster-whisper kurulu degil"

    durum = f"âœ… faster-whisper: {fw_version}\n"
    durum += f"âœ… Model: {VARSAYILAN_MODEL} (cpu, int8)\n"
    durum += f"âœ… Varsayilan dil: {VARSAYILAN_DIL}\n"

    if _WHISPER_MODEL is not None:
        durum += "âœ… Model su an RAM'de (yuklu)"
    else:
        durum += "â³ Model henuz yuklenmedi (ilk kullanimda yuklenecek)"

    return durum


# â”€â”€ Motor kayit â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_kaydet(motor: Any) -> None:
    """Motor'a STT araclarini kaydet."""

    def _stt_cevir(ses_yolu: str, dil: str = VARSAYILAN_DIL) -> str:
        """STT_CEVIR: Ses dosyasini metne cevir.

        Parametreler:
            ses_yolu (str, zorunlu) â€” Ses dosyasi yolu (.mp3, .wav, .ogg).
            dil (str, opsiyonel) â€” Dil kodu (varsayilan: 'tr').

        Doner: Transkripsiyon metni.
        """
        return sesi_metne_cevir(ses_yolu, dil)

    def _stt_durum() -> str:
        """STT_DURUM: STT sistem durumu."""
        return stt_durum()

    def _stt_test(ses_yolu: str = "") -> str:
        """STT_TEST: STT sistemini test et.

        Parametre:
            ses_yolu (str, opsiyonel) â€” Test edilecek ses dosyasi.
            Bos birakilirsa sadece model yuklemesini test eder.
        """
        try:
            model = _model_yukle()
            if ses_yolu:
                sonuc = sesi_metne_cevir(ses_yolu)
                if sonuc.startswith("[HATA]") or sonuc.startswith("[UYARI]"):
                    return f"âŒ STT test basarisiz: {sonuc}"
                return f'âœ… STT test basarili: "{sonuc[:100]}"'
            return "âœ… STT modeli yuklu, test icin bir ses dosyasi yolu verin."
        except Exception as e:
            return f"âŒ STT test basarisiz: {e}"

    if hasattr(motor, "_plugin_arac_kaydet"):
        motor._plugin_arac_kaydet(
            "STT_CEVIR",
            _stt_cevir,
            "Ses dosyasini metne cevirir (faster-whisper). "
            "Parametreler: ses_yolu (str, zorunlu) â€” ses dosyasi yolu; "
            "dil (str, opsiyonel) â€” dil kodu (varsayilan: 'tr'). "
            "Doner: transkripsiyon metni.",
        )
        motor._plugin_arac_kaydet(
            "STT_DURUM",
            _stt_durum,
            "STT sistem durumunu gosterir: model, dil, yuk durumu.",
        )
        motor._plugin_arac_kaydet(
            "STT_TEST",
            _stt_test,
            "STT sistemini test eder. "
            "Parametre: ses_yolu (str, opsiyonel) â€” test ses dosyasi.",
        )

        logger.info("[STT] Motor araclari kaydedildi: STT_CEVIR, STT_DURUM, STT_TEST")


if __name__ == "__main__":
    print(stt_durum())
