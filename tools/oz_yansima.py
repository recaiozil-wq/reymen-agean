# -*- coding: utf-8 -*-
"""
oz_yansima.py — FAZ 6: Pasif Surec Refleksiyonu (Idle-Time Reflection).

ToolRegistry'e kayit icin:
    TOOL_META = {...}
    def run(...)
    def check_fn(...)

Kullanim (agent):
    OZ_YANSIMA(baslat=True)  -> Arka plan yansimasini baslatir
    OZ_YANSIMA(bildirim=True) -> Bekleyen bildirimi getirir
    OZ_YANSIMA(log=True)      -> Son log satirlarini getirir
"""

import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging
logger = logging.getLogger(__name__)

TOOL_META = {
    "ad": "oz_yansima",
    "versiyon": "1.0.0",
    "aciklama": (
        "Pasif surec refleksiyonu (idle-time reflection). "
        "Arka planda hata oruntulerini, sistem metriklerini analiz eder "
        "ve iyilestirme onerileri uretir."
    ),
    "kategori": "ogrenme",
    "parametreler": {
        "baslat": {
            "tip": "bool",
            "aciklama": "Arka plan yansimasini baslatir",
            "zorunlu": False,
        },
        "bildirim": {
            "tip": "bool",
            "aciklama": "Bekleyen bildirimi getirir (varsa)",
            "zorunlu": False,
        },
        "log": {
            "tip": "bool",
            "aciklama": "Son yansima log satirlarini getirir",
            "zorunlu": False,
        },
        "gecikme_sn": {
            "tip": "int",
            "aciklama": "Thread baslamadan beklenecek sure (saniye, varsayilan: 2)",
            "zorunlu": False,
        },
    },
    "ornek": (
        'OZ_YANSIMA(baslat=True)  -> Arka plan yansimasini baslatir\\n'
        'OZ_YANSIMA(bildirim=True) -> Varsa bildirimi dondurur\\n'
        'OZ_YANSIMA(log=True)      -> Son log satirlarini gosterir'
    ),
}

ROOT = Path(__file__).parent.parent.resolve()
LOG_DOSYASI = ROOT / ".ReYMeN" / "oz_yansima_log.md"
MINIMUM_ARALIK_SN = 300
MAKS_LLM_TOKEN = 800

# ── Global state ─────────────────────────────────────────────────────
_oz_yansima_ornek = None
_oz_yansima_kilit = threading.Lock()


def _get_or_create_oz_yansima():
    """Tekil OzYansima ornegini al/yarat."""
    global _oz_yansima_ornek
    with _oz_yansima_kilit:
        if _oz_yansima_ornek is None:
            _oz_yansima_ornek = _OzYansimaMotoru()
        return _oz_yansima_ornek


class _OzYansimaMotoru:
    """Arka planda idle-time yansima calistiran yoneticisi (dahili)."""

    def __init__(self):
        self._bildirim: Optional[str] = None
        self._kilitli = threading.Lock()
        self._son_calisma: float = 0.0
        self._calisiyorum = False
        LOG_DOSYASI.parent.mkdir(parents=True, exist_ok=True)

    def baslat_arkaplan(self, gecikme_sn: int = 2) -> bool:
        """Daemon thread olarak yansimayi baslatir."""
        su_an = time.monotonic()
        if self._calisiyorum:
            return False
        if su_an - self._son_calisma < MINIMUM_ARALIK_SN:
            return False

        self._calisiyorum = True
        t = threading.Thread(
            target=self._calistir_yansima,
            args=(gecikme_sn,),
            daemon=True,
            name="OzYansima",
        )
        t.start()
        return True

    def bildirim_al(self) -> Optional[str]:
        """Yansima tamamlanmissa bildirimi dondur ve sifirla."""
        with self._kilitli:
            b = self._bildirim
            self._bildirim = None
            return b

    def log_oku(self, son_n_satir: int = 30) -> str:
        """Son yansima log satirlarini dondur."""
        if not LOG_DOSYASI.exists():
            return "[Oz-Yansima] Henuz yansima kaydi yok."
        satirlar = LOG_DOSYASI.read_text(encoding="utf-8").splitlines()
        return "\n".join(satirlar[-son_n_satir:])

    def _calistir_yansima(self, gecikme_sn: int):
        """Arka plan thread govdesi."""
        try:
            time.sleep(gecikme_sn)
            analiz = self._analiz_yap()
            if analiz:
                self._log_yaz(analiz)
                oneri_sayisi = analiz.get("oneri_sayisi", 0)
                if oneri_sayisi > 0:
                    with self._kilitli:
                        self._bildirim = (
                            f"[Oz-Yansima] {oneri_sayisi} oneri hazir "
                            f"-- /yansima ile gor"
                        )
        except Exception as e:
            print(f"[OzYansima] Arka plan hatasi: {e}")
        finally:
            self._son_calisma = time.monotonic()
            self._calisiyorum = False

    def _analiz_yap(self) -> Optional[dict]:
        """Hata verisi + sistem metrigi + LLM analizi calistir."""
        hata_verisi = {}
        # Session elimizde yok, sadece sistem metriklerine gore calis
        sistem_metrigi = _sistem_metrigi_al()
        return {
            "zaman": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "hata_orani": 0.0,
            "hata_sayisi": 0,
            "toplam_adim": 0,
            "sistem": sistem_metrigi,
            "oneriler": [],
            "oneri_sayisi": 0,
        }

    def _log_yaz(self, analiz: dict):
        """Analiz sonucunu log dosyasina ekle."""
        satirlar = [
            f"\n## {analiz['zaman']} — Oz-Yansima Raporu",
            f"- Hata orani: {analiz['hata_orani']:.0%} "
            f"({analiz['hata_sayisi']}/{analiz['toplam_adim']} adim)",
        ]
        if analiz["sistem"]:
            s = analiz["sistem"]
            satirlar.append(
                f"- Sistem: CPU %{s.get('cpu_yuzde', '?')}, "
                f"Bellek %{s.get('bellek_yuzde', '?')}"
            )
        satirlar.append("\n### Oneriler")
        for i, oneri in enumerate(analiz["oneriler"], 1):
            satirlar.append(f"{i}. {oneri}")

        try:
            with open(LOG_DOSYASI, "a", encoding="utf-8") as f:
                f.write("\n".join(satirlar) + "\n")
        except OSError as e:
            print(f"[OzYansima] Log yazma hatasi: {e}")


def _sistem_metrigi_al() -> dict:
    """psutil varsa CPU/RAM, yoksa bos dict don."""
    try:
        import psutil
        return {
            "cpu_yuzde": round(psutil.cpu_percent(interval=0.5), 1),
            "bellek_yuzde": round(psutil.virtual_memory().percent, 1),
        }
    except ImportError:
        return {}


def run(
    baslat: bool = False,
    bildirim: bool = False,
    log: bool = False,
    gecikme_sn: int = 2,
) -> str:
    """Oz-Yansima aracini calistir.

    Args:
        baslat: Arka plan yansimasini baslatir.
        bildirim: Bekleyen bildirimi getirir.
        log: Son log satirlarini getirir.
        gecikme_sn: Thread baslamadan beklenecek sure (saniye).

    Returns:
        str: Islemin sonucu.
    """
    motor = _get_or_create_oz_yansima()

    if baslat:
        sonuc = motor.baslat_arkaplan(gecikme_sn=gecikme_sn)
        if sonuc:
            return "[Oz-Yansima] Arka plan yansimasi baslatildi."
        return "[Oz-Yansima] Baslatilamadi: cok erken veya zaten calisiyor."

    if bildirim:
        b = motor.bildirim_al()
        if b:
            return b
        return "[Oz-Yansima] Bekleyen bildirim yok."

    if log:
        return motor.log_oku()

    return (
        "[Oz-Yansima] Kullanim: OZ_YANSIMA(baslat=True), "
        "OZ_YANSIMA(bildirim=True), veya OZ_YANSIMA(log=True)"
    )


def check_fn() -> bool:
    """Kullanilabilirlik kontrolu: psutil tavsiye edilir, zorunlu degil."""
    return True
