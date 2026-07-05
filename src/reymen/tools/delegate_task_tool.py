# -*- coding: utf-8 -*-
"""
delegate_task_tool.py â€” ThreadPoolExecutor-based parallel sub-agent delegation.

Inspired by the parallel task delegation system in ReYMeN Agent.
Runs sub-agents in parallel using ThreadPoolExecutor, gives each a separate
Beyin instance, collects results and summarizes.

Usage:
    DELEGATE_TASK(
        "gÃ¶rev_tanÄ±mlarÄ±_json",
        "baÄŸlam",
        max_paralel=3,
        timeout=60
    )

    gÃ¶rev_tanÄ±mlarÄ±_json = [
        {"gorev": "Dosya oku ve Ã¶zetle", "baglam": "dosya: test.py"},
        {"gorev": "Web'de ara", "baglam": "konu: yapay zeka"},
    ]

Dependencies:
    - concurrent.futures.ThreadPoolExecutor (standard library)
    - reymen.cereyan.beyin.Beyin
"""

from __future__ import annotations

import json
import logging
import os
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# â”€â”€ VarsayÄ±lan yapÄ±landÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_MAX_PARALEL = int(os.environ.get("DELEGATE_MAX_PARALEL", "5"))
_TIMEOUT = int(os.environ.get("DELEGATE_TIMEOUT", "120"))
_MAX_ADIM = int(os.environ.get("DELEGATE_MAX_ADIM", "10"))

# Proje kÃ¶kÃ¼ â†’ config.yaml yÃ¼kleme
_PROJE_KOK = Path(__file__).resolve().parent.parent.parent
_CONFIG_YOLU = _PROJE_KOK / "config.yaml"


def _config_yukle() -> dict:
    """Load project config.yaml, return empty dict if missing."""
    try:
        import yaml

        if _CONFIG_YOLU.exists():
            with open(_CONFIG_YOLU, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
    except Exception:
        logger.warning("[fix_01_sessiz_except] Exception")
    return {
        "default_provider": "lmstudio",
        "default_model": "cognitivecomputations.dolphin3.0-llama3.1-8b",
    }


_DELEGATE_CONFIG = _config_yukle()


@dataclass
class AltGorevSonuc:
    """Holds the result of a single sub-task."""

    gorev: str
    task_id: str
    basarili: bool
    sonuc: str = ""
    hata: str = ""
    sure_sn: float = 0.0
    adim_sayisi: int = 0


@dataclass
class DelegasyonSonuc:
    """TÃ¼m delegasyonun toplu sonucu."""

    parent_task_id: str
    toplam_gorev: int
    basarili: int
    basarisiz: int
    sonuclar: List[AltGorevSonuc] = field(default_factory=list)
    toplam_sure_sn: float = 0.0
    ozet: str = ""


def _alt_gorev_calistir(
    gorev: str,
    baglam: str,
    task_id: str,
    timeout: float,
    max_adim: int,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> AltGorevSonuc:
    """Tek bir alt gÃ¶revi Ã§alÄ±ÅŸtÄ±r (ThreadPoolExecutor worker'Ä±).

    Her alt gÃ¶rev:
    - Kendi Beyin instance'Ä±nÄ± alÄ±r (ana ajandan baÄŸÄ±msÄ±z)
    - Kendi ReAct dÃ¶ngÃ¼sÃ¼nÃ¼ Ã§alÄ±ÅŸtÄ±rÄ±r
    - Sonucu dÃ¶ndÃ¼rÃ¼r

    Zaman aÅŸÄ±mÄ± ve hata durumlarÄ±nÄ± yÃ¶netir.
    """
    baslangic = time.time()
    sonuc = AltGorevSonuc(
        gorev=gorev,
        task_id=task_id,
        basarili=False,
    )

    try:
        # Lazy import â€” sadece gerektiÄŸinde yÃ¼klenir
        from reymen.cereyan.beyin import Beyin

        # Alt ajan iÃ§in ayrÄ± Beyin (proje config'inden)
        beyin = Beyin(config=_DELEGATE_CONFIG)

        # Sistem promptu: alt ajan iÃ§in kÄ±sa ReAct talimatÄ±
        sistem_prompt = (
            f"Sen {task_id} ID'li bir ALT AJANSIN. "
            f"GÃ¶revi tamamlamak iÃ§in kÄ±sa ve Ã¶z cevap ver.\n\n"
            f"GÃ–REV: {gorev}\n"
            f"BAÄLAM: {baglam or '(verilmedi)'}\n\n"
            f"KURALLAR:\n"
            f"- DoÄŸrudan cevap yaz, araÃ§ kullanmana gerek yok.\n"
            f"- TÃ¼rkÃ§e cevap ver.\n"
            f"- En fazla {max_adim} adÄ±mÄ±n var.\n"
            f"- GOREV_BITTI ile bitir.\n"
        )

        mesajlar = [
            {"role": "system", "content": sistem_prompt},
            {"role": "user", "content": f"GÃ¶rev: {gorev}\nBaÄŸlam: {baglam}"},
        ]

        adim = 0
        while adim < max_adim:
            adim += 1
            gecen = time.time() - baslangic
            if gecen > timeout:
                sonuc.sonuc = f"(zaman_aÅŸÄ±mÄ±={timeout}s)"
                break

            # LLM Ã§aÄŸrÄ±sÄ±
            yanit = beyin.uret(sistem_prompt[:500], mesajlar)
            if not yanit:
                sonuc.sonuc = "(boÅŸ_yanÄ±t)"
                break

            mesajlar.append({"role": "assistant", "content": yanit})

            # GOREV_BITTI kontrolÃ¼
            if "GOREV_BITTI" in yanit:
                import re

                m = re.search(r'GOREV_BITTI\s*\(\s*"([^"]*)"\s*\)', yanit)
                sonuc.sonuc = m.group(1) if m else yanit
                break

            # BITTI: kontrolÃ¼
            if yanit.strip().startswith("BITTI:"):
                sonuc.sonuc = yanit.split("BITTI:", 1)[1].strip()
                break

            # Son adÄ±mda yanÄ±tÄ± sonuÃ§ olarak al
            if adim >= max_adim:
                sonuc.sonuc = yanit[:1000]

            # Devam mesajÄ±
            mesajlar.append(
                {
                    "role": "user",
                    "content": 'Devam et. Hedefe ulaÅŸtÄ±ysan GOREV_BITTI("cevap") yaz.',
                }
            )

        sonuc.basarili = True
        sonuc.adim_sayisi = adim

    except Exception as e:
        sonuc.hata = f"{type(e).__name__}: {e}"
        logger.warning("[delegate_task] Alt gÃ¶rev hatasÄ± (%s): %s", task_id, e)

    finally:
        sonuc.sure_sn = round(time.time() - baslangic, 2)

    return sonuc


def _delegate_task_impl(
    gorev_listesi: List[Dict[str, str]],
    baglam_genel: str = "",
    max_paralel: int = _MAX_PARALEL,
    timeout: float = _TIMEOUT,
    max_adim: int = _MAX_ADIM,
    provider: Optional[str] = None,
    model: Optional[str] = None,
) -> DelegasyonSonuc:
    """ThreadPoolExecutor ile alt gÃ¶revleri paralel Ã§alÄ±ÅŸtÄ±r.

    Args:
        gorev_listesi: Her biri {"gorev": str, "baglam": str} olan dict listesi.
        baglam_genel: TÃ¼m alt gÃ¶revlere eklenecek genel baÄŸlam.
        max_paralel: AynÄ± anda Ã§alÄ±ÅŸacak maksimum alt ajan sayÄ±sÄ±.
        timeout: Her alt gÃ¶rev iÃ§in maksimum sÃ¼re (saniye).
        max_adim: Her alt gÃ¶rev iÃ§in maksimum adÄ±m sayÄ±sÄ±.
        provider: Alt ajanlar iÃ§in provider (opsiyonel).
        model: Alt ajanlar iÃ§in model (opsiyonel).

    Returns:
        DelegasyonSonuc â€” tÃ¼m sonuÃ§larÄ± ve Ã¶zeti iÃ§erir.
    """
    parent_id = str(uuid.uuid4())[:8]
    baslangic = time.time()

    if not gorev_listesi:
        return DelegasyonSonuc(
            parent_task_id=parent_id,
            toplam_gorev=0,
            basarili=0,
            basarisiz=0,
            ozet="HiÃ§ gÃ¶rev tanÄ±mlanmamÄ±ÅŸ.",
        )

    sonuc = DelegasyonSonuc(
        parent_task_id=parent_id,
        toplam_gorev=len(gorev_listesi),
        basarili=0,
        basarisiz=0,
    )

    # ThreadPoolExecutor ile paralel Ã§alÄ±ÅŸtÄ±r
    with ThreadPoolExecutor(max_workers=max_paralel) as executor:
        future_map = {}
        for i, g in enumerate(gorev_listesi):
            gorev = g.get("gorev", "").strip()
            baglam = g.get("baglam", "").strip()
            if not gorev:
                continue

            # Genel baÄŸlamÄ± ekle
            if baglam_genel:
                baglam = f"{baglam_genel} | {baglam}" if baglam else baglam_genel

            task_id = f"{parent_id}-{i:03d}"

            future = executor.submit(
                _alt_gorev_calistir,
                gorev=gorev,
                baglam=baglam,
                task_id=task_id,
                timeout=timeout,
                max_adim=max_adim,
                provider=provider,
                model=model,
            )
            future_map[future] = task_id

        # SonuÃ§larÄ± topla
        for future in as_completed(future_map, timeout=timeout + 10):
            task_id = future_map[future]
            try:
                alt_sonuc = future.result(timeout=5)
                sonuc.sonuclar.append(alt_sonuc)
                if alt_sonuc.basarili:
                    sonuc.basarili += 1
                else:
                    sonuc.basarisiz += 1
            except Exception as e:
                sonuc.basarisiz += 1
                sonuc.sonuclar.append(
                    AltGorevSonuc(
                        gorev="(bilinmiyor)",
                        task_id=task_id,
                        basarili=False,
                        hata=f"Future hatasÄ±: {e}",
                    )
                )

    sonuc.toplam_sure_sn = round(time.time() - baslangic, 2)

    # Ã–zet oluÅŸtur
    sonuc.ozet = _ozet_olustur(sonuc)
    return sonuc


def _ozet_olustur(ds: DelegasyonSonuc) -> str:
    """Delegasyon sonucundan okunabilir bir Ã¶zet oluÅŸtur."""
    basarili_yuzde = round(
        (ds.basarili / ds.toplam_gorev * 100) if ds.toplam_gorev > 0 else 0
    )

    satirlar = [
        f"ğŸ“‹ DELEGASYON Ã–ZETÄ° (ID: {ds.parent_task_id})",
        f"  â±  SÃ¼re: {ds.toplam_sure_sn:.1f}s",
        f"  ğŸ“Š Toplam: {ds.toplam_gorev} gÃ¶rev",
        f"  âœ… BaÅŸarÄ±lÄ±: {ds.basarili} ({basarili_yuzde}%)",
        f"  âŒ BaÅŸarÄ±sÄ±z: {ds.basarisiz}",
        "",
    ]

    if ds.sonuclar:
        satirlar.append("GÃ¶rev SonuÃ§larÄ±:")
        for s in ds.sonuclar:
            ikon = "âœ…" if s.basarili else "âŒ"
            sonuc_ozet = (s.sonuc or s.hata or "-")[:150]
            satirlar.append(f"  {ikon} [{s.task_id}] {s.gorev[:60]}")
            satirlar.append(f"     â†’ {sonuc_ozet}")
            satirlar.append(f"     â± {s.sure_sn}s / {s.adim_sayisi} adÄ±m")

    return "\n".join(satirlar)


# â”€â”€ Ana fonksiyon: LLM'den Ã§aÄŸrÄ±lÄ±r â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def delegate_task(
    gorev_tanimlari: str,
    baglam_genel: str = "",
    max_paralel: int = _MAX_PARALEL,
    timeout: int = _TIMEOUT,
    max_adim: int = _MAX_ADIM,
) -> str:
    """Alt ajanlarÄ± ThreadPoolExecutor ile paralel Ã§alÄ±ÅŸtÄ±rÄ±r.

    Her alt ajan kendi Beyin instance'Ä±nÄ± kullanÄ±r, ayrÄ± bir conversation
    baÄŸlamÄ±nda Ã§alÄ±ÅŸÄ±r. TÃ¼m sonuÃ§lar toplanÄ±r ve Ã¶zetlenir.

    Args:
        gorev_tanimlari: JSON string. Her biri {"gorev": "...", "baglam": "..."}
                         olan bir dizi. Ã–rnek:
                         [{"gorev": "Dosya oku", "baglam": "test.py"},
                          {"gorev": "Web ara", "baglam": "yapay zeka"}]
        baglam_genel: TÃ¼m alt gÃ¶revlere eklenecek genel baÄŸlam (opsiyonel).
        max_paralel: AynÄ± anda Ã§alÄ±ÅŸacak maksimum alt ajan sayÄ±sÄ± (varsayÄ±lan: 5).
        timeout: Her alt gÃ¶rev iÃ§in maksimum sÃ¼re, saniye (varsayÄ±lan: 120).
        max_adim: Her alt gÃ¶rev iÃ§in maksimum adÄ±m sayÄ±sÄ± (varsayÄ±lan: 10).

    Returns:
        Ã–zet metin â€” tÃ¼m alt ajan sonuÃ§larÄ±nÄ±n okunabilir Ã¶zeti.
    """
    try:
        # JSON parse
        if isinstance(gorev_tanimlari, str):
            gorev_listesi = json.loads(gorev_tanimlari)
        else:
            gorev_listesi = gorev_tanimlari

        if not isinstance(gorev_listesi, list):
            return "âŒ HATA: gorev_tanimlari bir JSON dizi olmalÄ±."

        # Delegasyonu Ã§alÄ±ÅŸtÄ±r
        ds = _delegate_task_impl(
            gorev_listesi=gorev_listesi,
            baglam_genel=baglam_genel,
            max_paralel=max_paralel,
            timeout=timeout,
            max_adim=max_adim,
        )

        return ds.ozet

    except json.JSONDecodeError as e:
        return f"âŒ HATA: GeÃ§ersiz JSON formatÄ± â€” {e}"
    except Exception as e:
        logger.error("[delegate_task] Beklenmeyen hata: %s", e)
        logger.error(traceback.format_exc())
        return f"âŒ HATA: {type(e).__name__}: {e}"


# â”€â”€ Motor entegrasyonu â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_kaydet(motor) -> None:
    """Motor'a DELEGATE_TASK aracÄ±nÄ± kaydet.

    Bu fonksiyon, motor.py'nin _plugin_moduller_yukle() metodu tarafÄ±ndan
    otomatik Ã§aÄŸrÄ±lÄ±r. Tool tanÄ±mÄ±nÄ± ve fonksiyonunu motor'a bildirir.
    """
    motor._plugin_arac_kaydet(
        "DELEGATE_TASK",
        delegate_task,
        (
            "Alt ajanlarÄ± paralel Ã§alÄ±ÅŸtÄ±rÄ±r. "
            "Paralel alt-ajan sistemi: GÃ¶revleri ThreadPoolExecutor ile paralel Ã§alÄ±ÅŸtÄ±rÄ±r. "
            "Her alt ajan kendi Beyin instance'Ä±nÄ± kullanÄ±r, ayrÄ± bir conversation baÄŸlamÄ±nda Ã§alÄ±ÅŸÄ±r. "
            "TÃ¼m sonuÃ§lar toplanÄ±r ve Ã¶zetlenir.\n\n"
            "Parametreler:\n"
            "  gorev_tanimlari (str, ZORUNLU): JSON string. "
            'Her biri {"gorev": "...", "baglam": "..."} olan bir dizi.\n'
            "  baglam_genel (str, opsiyonel): TÃ¼m alt gÃ¶revlere eklenecek genel baÄŸlam.\n"
            "  max_paralel (int, opsiyonel): AynÄ± anda Ã§alÄ±ÅŸacak maksimum alt ajan sayÄ±sÄ± (varsayÄ±lan: 5).\n"
            "  timeout (int, opsiyonel): Her alt gÃ¶rev iÃ§in maksimum sÃ¼re (varsayÄ±lan: 120s).\n"
            "  max_adim (int, opsiyonel): Her alt gÃ¶rev iÃ§in maksimum adÄ±m (varsayÄ±lan: 10).\n\n"
            "Ã–rnek:\n"
            '  DELEGATE_TASK(\'[{"gorev":"DosyayÄ± oku ve Ã¶zetle","baglam":"test.py"},'
            '{"gorev":"Web ara","baglam":"yapay zeka"}]\')'
        ),
    )


# â”€â”€ DoÄŸrudan Ã§alÄ±ÅŸtÄ±rma testi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    # Test: basit delegasyon
    test_gorevler = json.dumps(
        [
            {"gorev": "Merhaba dÃ¼nya yaz", "baglam": ""},
            {"gorev": "2+2 kaÃ§ eder?", "baglam": "matematik"},
        ]
    )
    sonuc = delegate_task(test_gorevler, max_paralel=2, timeout=30, max_adim=3)
    print(sonuc)
