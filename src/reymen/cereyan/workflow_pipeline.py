# -*- coding: utf-8 -*-
"""
workflow_pipeline.py â€” GÃ¶rev Ã‡Ã¶zÃ¼m Pipeline'Ä±.

GÃ–REV -> PLANLAMA -> Ã–N DOÄRULAMA -> KOD -> TEST -> GÃ–ZDEN GEÃ‡Ä°RME -> KAYDET

Her aÅŸama broker Ã¼zerinden mesajlaÅŸÄ±r. Consumer thread'lerde Ã§alÄ±ÅŸÄ±r.
Mevcut sistemdeki orchestrator + ogrenme + hata_cozucu'yu birleÅŸtirir.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from reymen.cereyan.broker import (
    Mesaj,
    MesajTipi,
    MessageBroker,
    get_broker,
    mesaj_gonder,
)

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent.parent.resolve()
SCRIPTS_DIR = ROOT / "reymen" / "scripts"
COKLER_DIR = ROOT / "cozumler"


# â”€â”€ Handler'lar (consumer callback'leri) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def hata_handler(mesaj: Mesaj) -> None:
    """HATA mesajÄ± â†’ hata_cozucu'ya yÃ¶nlendir."""
    veri = mesaj.veri
    hata = veri.get("hata", "")
    kod = veri.get("kod", "")
    kaynak = veri.get("kaynak", "")
    hata_imza = _imza_uret_string(hata)

    logger.info("[Pipeline] HATA handler: %s...", str(hata)[:100])

    # Ã–nce Ã§Ã¶zÃ¼m hafÄ±zasÄ±nda ara
    try:
        from reymen.core.ogrenme import cozum_bul, imza_uret, cozum_kaydet

        bulunan = cozum_bul(hata_imza)
        if bulunan:
            logger.info("[Pipeline] Ã‡Ã¶zÃ¼m hafÄ±zada bulundu: %s", hata_imza[:12])
            broker = get_broker()
            if broker:
                broker.yayinla_basit(
                    MesajTipi.COZUM_BULUNDU,
                    {
                        "cozum": bulunan,
                        "correlation_id": mesaj.correlation_id,
                    },
                )
            return
    except ImportError:
        logger.debug("[Pipeline] ogrenme modÃ¼lÃ¼ yok, LLM'e gidilecek")
    except Exception as e:
        logger.warning("[Pipeline] HafÄ±za sorgu hatasÄ±: %s", e)

    # HafÄ±zada yoksa â†’ orchestrator'a LLM Ã§Ã¶zÃ¼mÃ¼ iÃ§in yÃ¶nlendir
    try:
        _coz = None
        try:
            from reymen.core.orchestrator import coz_hata

            _coz = coz_hata
        except ImportError as _e:
            logger.warning(
                "[WorkflowPipeline] Modul yuklenemedi (L71): %s", ImportError
            )
            pass

        if _coz:
            fix_kod = _coz(hata, kod, kaynak or "pipeline")
            if fix_kod and kod:
                # Fix script'ini kaydet
                fix_dizini = COKLER_DIR / "fix"
                fix_dizini.mkdir(parents=True, exist_ok=True)
                fix_path = fix_dizini / f"fix_{datetime.now():%Y%m%d_%H%M%S}.py"
                fix_path.write_text(fix_kod, encoding="utf-8")
                logger.info("[Pipeline] Fix kaydedildi: %s", fix_path)

                # Ã‡Ã¶zÃ¼mÃ¼ hafÄ±zaya kaydet
                try:
                    from reymen.core.ogrenme import cozum_kaydet as _kaydet

                    _kaydet(
                        hata_imza, "pipeline", hata[:200], fix_kod, str(fix_path), True
                    )
                except Exception as _e:
                    logger.warning(
                        "[WorkflowPipeline] except Exception (L88): %s", Exception
                    )
                    pass

                broker = get_broker()
                if broker:
                    broker.yayinla_basit(
                        MesajTipi.COZUM_BULUNDU,
                        {
                            "cozum": fix_kod,
                            "path": str(fix_path),
                            "correlation_id": mesaj.correlation_id,
                        },
                    )
    except Exception as e:
        logger.error("[Pipeline] coz_hata baÅŸarÄ±sÄ±z: %s", e)


def cozum_ara_handler(mesaj: Mesaj) -> None:
    """COZUM_ARA mesajÄ± â†’ ogrenme.cozum_bul."""
    veri = mesaj.veri
    hata = veri.get("hata", "")
    hata_imza = _imza_uret_string(hata)

    try:
        from reymen.core.ogrenme import cozum_bul

        bulunan = cozum_bul(hata_imza)
        if bulunan:
            logger.info("[Pipeline] Ã‡Ã¶zÃ¼m bulundu: %s", hata_imza[:12])
            broker = get_broker()
            if broker:
                broker.yayinla_basit(
                    MesajTipi.COZUM_BULUNDU,
                    {
                        "cozum": bulunan,
                        "imza": hata_imza,
                        "correlation_id": mesaj.correlation_id,
                    },
                )
    except Exception as e:
        logger.debug("[Pipeline] cozum_ara hatasÄ±: %s", e)


def cozum_kaydet_handler(mesaj: Mesaj) -> None:
    """COZUM_KAYDET mesajÄ± â†’ ogrenme.cozum_kaydet + closed_learning_loop."""
    veri = mesaj.veri
    try:
        from reymen.core.ogrenme import cozum_kaydet

        cozum_kaydet(
            imza=veri.get("imza", ""),
            hata_tipi=veri.get("hata_tipi", "pipeline"),
            hata_ozet=veri.get("ozet", "")[:500],
            cozum_kodu=veri.get("cozum", ""),
            kaynak_script=veri.get("kaynak", ""),
            basarili=veri.get("basarili", True),
        )
        logger.info("[Pipeline] Ã‡Ã¶zÃ¼m hafÄ±zaya kaydedildi")
    except Exception as e:
        logger.warning("[Pipeline] cozum_kaydet hatasÄ±: %s", e)

    # closed_learning_loop'a da bildir
    try:
        from reymen.cereyan.closed_learning_loop import ClosedLearningLoop

        loop = ClosedLearningLoop()
        loop.beceri_kristallestir(
            beceri_adi=veri.get("ad", "otonom_cozum"),
            aciklama=veri.get("ozet", "")[:200],
            adimlar=veri.get("cozum", "")[:500],
        )
    except Exception as _e:
        logger.warning("[WorkflowPipeline] except Exception (L150): %s", Exception)
        pass


# â”€â”€ Workflow Pipeline â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def gorev_coz_pipeline(
    broker: MessageBroker, gorev_tanimi: str, script_path: str = ""
) -> str:
    """
    Ana pipeline: GÃ–REV -> PLANLA -> Ã–N DOÄRULA -> KOD -> TEST -> Ä°NCELE -> KAYDET

    Args:
        broker: MessageBroker instance
        gorev_tanimi: GÃ¶rev aÃ§Ä±klamasÄ±
        script_path: Varsa mevcut script yolu

    Returns:
        BaÅŸarÄ±lÄ±ysa ".py" dosya yolu, baÅŸarÄ±sÄ±zsa hata mesajÄ±
    """
    corr_id = os.urandom(6).hex()
    logger.info("[Pipeline] â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•")
    logger.info("[Pipeline] GÃ–REV BAÅLAT: %s", gorev_tanimi[:100])

    current_script = script_path

    # â”€â”€ ADIM 1: PLANLAMA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logger.info("[Pipeline] ADIM 1/6: PLANLAMA")
    plan = _pipeline_planla(gorev_tanimi)
    if not plan:
        return "âŒ PLANLAMA BAÅARISIZ"

    # â”€â”€ ADIM 2: Ã–N DOÄRULAMA â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logger.info("[Pipeline] ADIM 2/6: Ã–N DOÄRULAMA")
    dogrulama = _pipeline_on_dogrula(plan)
    if not dogrulama.get("gecerli"):
        return f"âŒ Ã–N DOÄRULAMA: {dogrulama.get('sebep', 'bilinmiyor')}"

    # â”€â”€ ADIM 3: KOD â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logger.info("[Pipeline] ADIM 3/6: KOD ÃœRETÄ°MÄ°")
    if not current_script or not Path(current_script).exists():
        current_script = _pipeline_kod_uret(plan, gorev_tanimi)
        if not current_script:
            return "âŒ KOD ÃœRETÄ°LEMEDÄ°"

    # â”€â”€ ADIM 4: TEST â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logger.info("[Pipeline] ADIM 4/6: TEST")
    test_sonuc = _pipeline_test_et(current_script)
    if not test_sonuc.get("basarili"):
        # Hata â†’ broker Ã¼zerinden Ã§Ã¶zÃ¼m dÃ¶ngÃ¼sÃ¼
        hata_msg = test_sonuc.get("hata", "bilinmiyor")
        broker.yayinla_basit(
            MesajTipi.HATA,
            {
                "hata": hata_msg,
                "kod": Path(current_script).read_text(encoding="utf-8")
                if Path(current_script).exists()
                else "",
                "kaynak": current_script,
            },
            kaynak="pipeline",
        )

        # Ã‡Ã¶zÃ¼m bekle (3 saniye)
        time.sleep(3)

        # Fix denenmiÅŸ olabilir, tekrar dene
        test_sonuc = _pipeline_test_et(current_script)
        if not test_sonuc.get("basarili"):
            return f"âŒ TEST: {hata_msg}"

    # â”€â”€ ADIM 5: GÃ–ZDEN GEÃ‡Ä°R â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logger.info("[Pipeline] ADIM 5/6: GÃ–ZDEN GEÃ‡Ä°RME")
    inceleme = _pipeline_gozden_gecir(current_script)
    if not inceleme.get("basarili"):
        logger.warning("[Pipeline] Ä°nceleme uyarÄ±sÄ±: %s", inceleme.get("uyari", ""))
        # Kritik deÄŸilse devam et

    # â”€â”€ ADIM 6: KAYDET â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    logger.info("[Pipeline] ADIM 6/6: KAYDET")
    kayit_path = _pipeline_kaydet(current_script, gorev_tanimi, corr_id)

    # BaÅŸarÄ±lÄ± mesajÄ±
    broker.yayinla_basit(
        MesajTipi.GOREV_BASARILI,
        {
            "path": kayit_path,
            "correlation_id": corr_id,
        },
        kaynak="pipeline",
    )

    # closed_learning_loop'a bildir
    try:
        from reymen.cereyan.closed_learning_loop import ClosedLearningLoop

        loop = ClosedLearningLoop()
        loop.beceri_kristallestir(
            beceri_adi=f"cozum_{corr_id}",
            aciklama=gorev_tanimi[:200],
            adimlar=Path(kayit_path).read_text(encoding="utf-8")[:500],
        )
    except Exception as _e:
        __import__("logging").getLogger(__name__).warning(
            "[SessizExcept] %%s: %%s", type(_e).__name__, _e
        )

    logger.info("[Pipeline] âœ… GÃ–REV TAMAM: %s", kayit_path)
    return kayit_path


# â”€â”€ Pipeline Alt AdÄ±mlarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _pipeline_planla(gorev: str) -> Optional[dict]:
    """ADIM 1: GÃ¶revi alt adÄ±mlara ayÄ±r."""
    return {
        "gorev": gorev[:200],
        "adimlar": ["hazirlik", "cozum", "dogrulama"],
        "hedef_dosya": f"cozum_{datetime.now():%Y%m%d_%H%M%S}.py",
    }


def _pipeline_on_dogrula(plan: dict) -> dict:
    """ADIM 2: Ã–n koÅŸullarÄ± kontrol et."""
    import shutil

    eksikler = []

    # Python kontrolÃ¼
    if not shutil.which("python"):
        eksikler.append("python")

    return {
        "gecerli": len(eksikler) == 0,
        "sebep": ", ".join(eksikler) if eksikler else "",
    }


def _pipeline_kod_uret(plan: dict, gorev: str) -> Optional[str]:
    """ADIM 3: LLM ile Python script'i Ã¼ret."""
    hedef = plan.get("hedef_dosya", "cozum.py")
    hedef_path = str(SCRIPTS_DIR / hedef)

    # LLM'den kod iste
    try:
        from reymen.core.orchestrator import ask_model_to_fix

        kod = ask_model_to_fix("", f"# GOREV: {gorev}\n# ")
        if kod and len(kod) > 10:
            SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
            Path(hedef_path).write_text(kod, encoding="utf-8")
            logger.info("[Pipeline] Kod Ã¼retildi: %s (%d byte)", hedef_path, len(kod))
            return hedef_path
    except Exception as e:
        logger.warning("[Pipeline] Kod Ã¼retimi baÅŸarÄ±sÄ±z: %s", e)

    return None


def _pipeline_test_et(script_path: str) -> dict:
    """ADIM 4: Script'i Ã§alÄ±ÅŸtÄ±r ve doÄŸrula."""
    path = Path(script_path)
    if not path.exists():
        return {"basarili": False, "hata": "Dosya bulunamadÄ±"}

    try:
        # Syntax kontrolÃ¼
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
    except SyntaxError as e:
        return {"basarili": False, "hata": f"SyntaxError: {e}"}

    try:
        # Import kontrolÃ¼ (dosya adÄ±nÄ± module olarak dene)
        import importlib.util

        spec = importlib.util.spec_from_file_location(path.stem, str(path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        return {"basarili": True, "cikti": ""}
    except Exception as e:
        return {"basarili": False, "hata": f"{type(e).__name__}: {e}"}


def _pipeline_gozden_gecir(script_path: str) -> dict:
    """ADIM 5: Kodu statik analiz ile gÃ¶zden geÃ§ir."""
    path = Path(script_path)
    if not path.exists():
        return {"basarili": False, "uyari": "Dosya yok"}

    kod = path.read_text(encoding="utf-8")
    uyarilar = []

    # Basit kalite kontrolleri
    if "except:" in kod and "except Exception" not in kod:
        uyarilar.append("Bare except tespit edildi")
    if len(kod) < 20:
        uyarilar.append("Kod Ã§ok kÄ±sa")

    return {
        "basarili": len(uyarilar) == 0,
        "uyari": "; ".join(uyarilar) if uyarilar else "",
    }


def _pipeline_kaydet(script_path: str, gorev: str, corr_id: str) -> str:
    """ADIM 6: BaÅŸarÄ±lÄ± script'i .py dosyasÄ±na kaydet."""
    hedef = COKLER_DIR / f"cozum_{corr_id}.py"
    hedef.parent.mkdir(parents=True, exist_ok=True)

    if Path(script_path).exists():
        import shutil

        shutil.copy2(script_path, hedef)
    else:
        hedef.write_text(f"# {gorev}\n# Correlation ID: {corr_id}\n", encoding="utf-8")

    return str(hedef)


# â”€â”€ YardÄ±mcÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def _imza_uret_string(hata_str: str) -> str:
    """String hata mesajÄ±ndan imza Ã¼ret."""
    import hashlib
    import re

    soyut = re.sub(r"'[^']*'", "'<VAL>'", str(hata_str))
    soyut = re.sub(r"\d+", "<N>", soyut)
    soyut = re.sub(r"/\S+", "/<PATH>", soyut)
    ham = f"pipeline:{soyut[:200]}"
    return hashlib.sha256(ham.encode()).hexdigest()[:16]


def _get_broker() -> Optional[MessageBroker]:
    try:
        from reymen.cereyan.broker import get_broker as _gb

        return _gb()
    except Exception:
        return None
