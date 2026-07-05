# -*- coding: utf-8 -*-
"""
gozlem.py â€” Katman 5: LLM Ã‡aÄŸrÄ± GÃ¶zlem ve Maliyet Takibi

Her LLM Ã§aÄŸrÄ±sÄ±nÄ±n token, sÃ¼re, maliyet bilgilerini task_id bazlÄ± kaydeder.
Ã‡oklu alt ajan sisteminde maliyetin sessizce patlamasÄ±nÄ± Ã¶nler.

KullanÄ±m:
    from gozlem import gozlemci
import logging
logger = logging.getLogger(__name__)
    gozlemci.kaydet("task_123", 2.5, "cevap metni", basarili=True)
    ozet = gozlemci.task_ozet("task_123")
    rapor = gozlemci.genel_ozet()
"""

import json
import os
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# â”€â”€ Sabitler â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

ROOT = Path(__file__).parent.resolve()
GOZLEM_DIZINI = ROOT / ".alt_ajan_gozlem"
DISK_LOG_LIMIT = 10000  # En fazla 10K satÄ±r
TOKEN_BASINA_MALIYET = {
    # $/1K token (girdi / Ã§Ä±ktÄ±) â€” yaklaÅŸÄ±k fiyatlar
    "deepseek": (0.0005, 0.0020),
    "openai": (0.00015, 0.0006),
    "anthropic": (0.00025, 0.00125),
    "groq": (0.0001, 0.0001),
    "lmstudio": (0.0, 0.0),  # Yerel, Ã¼cretsiz
    "ollama": (0.0, 0.0),  # Yerel, Ã¼cretsiz
}
VARSAYILAN_MALIYET = (0.001, 0.003)  # Tahmini ortalama


# â”€â”€ Veri YapÄ±larÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass
class GozlemKaydi:
    task_id: str
    sure_sn: float
    girdi_token: int = 0
    cikti_token: int = 0
    basarili: bool = True
    ts: float = field(default_factory=time.time)
    notlar: str = ""


class Gozlemci:
    """LLM Ã§aÄŸrÄ±larÄ±nÄ± gÃ¶zlemler, maliyeti hesaplar, diske loglar."""

    def __init__(self):
        self._kayitlar: list[GozlemKaydi] = []
        self._kilit = threading.Lock()
        self._task_sayac: dict[str, int] = defaultdict(int)
        self._task_maliyet: dict[str, float] = defaultdict(float)
        GOZLEM_DIZINI.mkdir(parents=True, exist_ok=True)

    def kaydet(
        self,
        task_id: str,
        sure_sn: float,
        cevap: str = "",
        basarili: bool = True,
        girdi_token: int = 0,
        cikti_token: int = 0,
        notlar: str = "",
    ) -> None:
        """Bir LLM Ã§aÄŸrÄ±sÄ±nÄ± kaydeder.

        Args:
            task_id: Hangi task'a ait
            sure_sn: Ã‡aÄŸrÄ± sÃ¼resi (saniye)
            cevap: LLM yanÄ±tÄ± (opsiyonel, token sayÄ±sÄ± iÃ§in)
            basarili: BaÅŸarÄ±lÄ± mÄ±?
            girdi_token: Girdi token sayÄ±sÄ± (biliniyorsa)
            cikti_token: Ã‡Ä±ktÄ± token sayÄ±sÄ± (biliniyorsa)
            notlar: Ek notlar
        """
        # Token sayÄ±sÄ±nÄ± tahmin et (bilinmiyorsa)
        if cikti_token == 0 and cevap:
            cikti_token = max(1, len(cevap) // 4)  # Kabaca: 4 karakter â‰ˆ 1 token

        kayit = GozlemKaydi(
            task_id=task_id,
            sure_sn=round(sure_sn, 3),
            girdi_token=girdi_token,
            cikti_token=cikti_token,
            basarili=basarili,
            notlar=notlar,
        )

        with self._kilit:
            self._kayitlar.append(kayit)
            self._task_sayac[task_id] += 1
            self._task_maliyet[task_id] += self._maliyet_hesapla(kayit)

        # Diske yaz (log)
        self._diske_yaz(kayit)

    def _maliyet_hesapla(self, kayit: GozlemKaydi) -> float:
        """Token bazlÄ± yaklaÅŸÄ±k maliyeti hesaplar ($ cinsinden)."""
        # Provider bilgisi yoksa varsayÄ±lan kullan
        g_maliyet, c_maliyet = VARSAYILAN_MALIYET
        maliyet = (kayit.girdi_token * g_maliyet + kayit.cikti_token * c_maliyet) / 1000
        return round(maliyet, 6)

    def _diske_yaz(self, kayit: GozlemKaydi) -> None:
        """CSV benzeri satÄ±rÄ± diske ekler."""
        satir = (
            f"{kayit.task_id}|{kayit.ts:.1f}|{kayit.sure_sn:.2f}|"
            f"{kayit.girdi_token}|{kayit.cikti_token}|"
            f"{'OK' if kayit.basarili else 'FAIL'}|{kayit.notlar}\n"
        )
        log_dosyasi = GOZLEM_DIZINI / "gozlem_log.txt"
        try:
            with open(log_dosyasi, "a", encoding="utf-8") as f:
                f.write(satir)
            # Log Ã§ok bÃ¼yÃ¼dÃ¼yse kÄ±rp
            if log_dosyasi.stat().st_size > DISK_LOG_LIMIT * 80:
                self._log_kirp(log_dosyasi)
        except OSError as _gozlem_e127:
            print(f"[UYARI] gozlem.py:128 - {_gozlem_e127}")

    def _log_kirp(self, dosya: Path):
        """Log dosyasÄ±nÄ± son N satÄ±ra kÄ±rp."""
        try:
            satirlar = dosya.read_text(encoding="utf-8").splitlines()
            if len(satirlar) > DISK_LOG_LIMIT:
                dosya.write_text(
                    "\n".join(satirlar[-DISK_LOG_LIMIT:]) + "\n",
                    encoding="utf-8",
                )
        except (OSError, UnicodeDecodeError) as _gozlem_e139:
            print(f"[UYARI] gozlem.py:140 - {_gozlem_e139}")

    def task_ozet(self, task_id: str) -> dict:
        """Bir task'Ä±n gÃ¶zlem Ã¶zetini dÃ¶ndÃ¼rÃ¼r."""
        with self._kilit:
            task_kayitlari = [k for k in self._kayitlar if k.task_id == task_id]
            if not task_kayitlari:
                return {"task_id": task_id, "cagri_sayisi": 0}

            toplam_sure = sum(k.sure_sn for k in task_kayitlari)
            basarili = sum(1 for k in task_kayitlari if k.basarili)
            toplam_girdi = sum(k.girdi_token for k in task_kayitlari)
            toplam_cikti = sum(k.cikti_token for k in task_kayitlari)

            return {
                "task_id": task_id,
                "cagri_sayisi": len(task_kayitlari),
                "toplam_sure_sn": round(toplam_sure, 2),
                "ortalama_sure_sn": round(toplam_sure / len(task_kayitlari), 2),
                "basarili": basarili,
                "basarisiz": len(task_kayitlari) - basarili,
                "toplam_girdi_token": toplam_girdi,
                "toplam_cikti_token": toplam_cikti,
                "tahmini_maliyet_usd": round(self._task_maliyet.get(task_id, 0), 6),
            }

    def genel_ozet(self) -> dict:
        """TÃ¼m gÃ¶zlemlerin Ã¶zetini dÃ¶ndÃ¼rÃ¼r."""
        with self._kilit:
            if not self._kayitlar:
                return {"toplam_cagri": 0, "aktif_task": 0, "tahmini_maliyet_usd": 0}

            toplam_sure = sum(k.sure_sn for k in self._kayitlar)
            basarili = sum(1 for k in self._kayitlar if k.basarili)
            toplam_girdi = sum(k.girdi_token for k in self._kayitlar)
            toplam_cikti = sum(k.cikti_token for k in self._kayitlar)
            toplam_maliyet = sum(self._task_maliyet.values())
            aktif_task = len(self._task_sayac)

            return {
                "toplam_cagri": len(self._kayitlar),
                "aktif_task": aktif_task,
                "toplam_sure_sn": round(toplam_sure, 2),
                "basarili": basarili,
                "basarisiz": len(self._kayitlar) - basarili,
                "basarili_yuzde": round(basarili / len(self._kayitlar) * 100, 1)
                if self._kayitlar
                else 0,
                "toplam_girdi_token": toplam_girdi,
                "toplam_cikti_token": toplam_cikti,
                "tahmini_maliyet_usd": round(toplam_maliyet, 4),
                "en_pahali_task": max(self._task_maliyet.items(), key=lambda x: x[1])[0]
                if self._task_maliyet
                else None,
            }

    def temizle(self):
        """TÃ¼m kayÄ±tlarÄ± temizle."""
        with self._kilit:
            self._kayitlar.clear()
            self._task_sayac.clear()
            self._task_maliyet.clear()


# â”€â”€ Singleton â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

gozlemci = Gozlemci()


# â”€â”€ Test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    gozlemci.kaydet("test_001", 2.5, "Merhaba dunya", basarili=True)
    gozlemci.kaydet("test_001", 1.2, "Nasilsin", basarili=True)
    gozlemci.kaydet("test_002", 0.5, "", basarili=False, notlar="TIMEOUT")

    ozet = gozlemci.task_ozet("test_001")
    assert ozet["cagri_sayisi"] == 2, "2 cagri olmali"
    print(f"[OK] Task ozet: {ozet['cagri_sayisi']} cagri, {ozet['toplam_sure_sn']}sn")

    genel = gozlemci.genel_ozet()
    assert genel["toplam_cagri"] == 3, "Toplam 3 cagri olmali"
    print(
        f"[OK] Genel ozet: {genel['toplam_cagri']} cagri, ${genel['tahmini_maliyet_usd']:.6f}"
    )

    # Disk log kontrolÃ¼
    log_path = GOZLEM_DIZINI / "gozlem_log.txt"
    if log_path.exists():
        satir_sayisi = len(log_path.read_text(encoding="utf-8").splitlines())
        print(f"[OK] Disk log: {satir_sayisi} satir")

    gozlemci.temizle()
    assert gozlemci.genel_ozet()["toplam_cagri"] == 0, "Temizlik sonrasi 0 olmali"
    print("[OK] Tum gozlem testleri gecti")
