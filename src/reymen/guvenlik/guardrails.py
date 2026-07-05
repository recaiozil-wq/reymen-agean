# -*- coding: utf-8 -*-
"""
guardrails.py â€” Hallucination filtreleme ve HITL sÄ±kÄ±laÅŸtÄ±rma.

Ä°ki bileÅŸen:
  1. HallucinationFiltresi
       LLM yanÄ±tÄ±nda risk iÅŸaretlerini (belirsiz dil, doÄŸrulanamaz iddia,
       yanlÄ±ÅŸ sÃ¼rÃ¼m referansÄ±, Ã¶z-referans halÃ¼sinasyon) tespit eder.
       YanÄ±tÄ± deÄŸiÅŸtirmez; yalnÄ±zca uyarÄ± listesi Ã¼retir.

  2. HITLSikistirici
       motor.ekstra_riskli kÃ¼mesini geniÅŸleterek ek araÃ§larÄ± HITL onayÄ±na alÄ±r.
       geri_al() ile eski kÃ¼me geri yÃ¼klenir.

KullanÄ±m::

    from guardrails import HallucinationFiltresi, HITLSikistirici

    filtre = HallucinationFiltresi()
    _, uyarilar = filtre.filtrele(yanit, hedef="dosya oluÅŸtur")

    hitl = HITLSikistirici(motor)
    hitl.sikilas()          # RISKLI kÃ¼mesine ek araÃ§lar ekle
    hitl.geri_al()          # eski hale dÃ¶ndÃ¼r
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# â”€â”€ Regex kalÄ±plarÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# Belirsiz / emin olmayan dil
_EMIN_OLMAYAN_KALIPLAR: list[str] = [
    r"\bsanÄ±r[Ä±m|Ä±z]?\b",
    r"\bgaliba\b",
    r"\btahmin\s+ediyorum\b",
    r"\bolabilir(?:im|siniz)?\b",
    r"\bbelki\b",
    r"\bdÃ¼ÅŸÃ¼nÃ¼yorum\s+ki\b",
    r"\byÃ¼ksek\s+ihtimalle?\b",
    r"\bmuhtemelen\b",
]

# DoÄŸrulanamayan kesin iddia
_KESIN_IDDIA_KALIPLARI: list[str] = [
    r"\bkesinlikle\b",
    r"\bmutlaka\b",
    r"\bher\s+zaman\s+(?:Ã§alÄ±ÅŸÄ±r|doÄŸru|iÅŸe\s+yarar)\b",
    r"\basla\s+(?:hata\s+vermez|Ã§Ã¶kmez|baÅŸarÄ±sÄ±z\s+olmaz)\b",
    r"\b%100\b",
    r"\bgarantili\b",
]

# Eski / yanlÄ±ÅŸ sÃ¼rÃ¼m referanslarÄ±
_YANLIS_SURUM_KALIPLARI: list[str] = [
    r"\bPython\s+[12]\.[0-9]\b",
    r"\bWindows\s+(?:3|9[58]|ME|XP)\b",
]

# LLM'in yapamayacaÄŸÄ± eylemleri yaptÄ±ÄŸÄ±nÄ± iddia etmesi
_OZ_REFERANS_KALIPLARI: list[str] = [
    r"\binternetle\s+(?:kontrol\s+ettim|baktÄ±m)\b",
    r"\baz\s+Ã¶nce\s+(?:indirdim|kurdum|yÃ¼kledim)\b",
    r"\bdiskinizdeki\b",
]

# Derleme â€” tek seferlik, modÃ¼l yÃ¼klenirken
_EMIN_OLMAYAN_RE = re.compile("|".join(_EMIN_OLMAYAN_KALIPLAR), re.IGNORECASE)
_KESIN_IDDIA_RE = re.compile("|".join(_KESIN_IDDIA_KALIPLARI), re.IGNORECASE)
_YANLIS_SURUM_RE = re.compile("|".join(_YANLIS_SURUM_KALIPLARI), re.IGNORECASE)
_OZ_REFERANS_RE = re.compile("|".join(_OZ_REFERANS_KALIPLARI), re.IGNORECASE)

# Uzun yanÄ±t eÅŸiÄŸi (karakter)
_UZUN_YANIT_ESIGI: int = 2500


# â”€â”€ UyarÄ± veri yapÄ±sÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


@dataclass(frozen=True)
class Uyari:
    """Tek bir hallucination uyarÄ±sÄ±."""

    kod: str  # Makine tarafÄ±ndan okunabilir tanÄ±mlayÄ±cÄ± (Ã¶r. "EMIN_OLMAYAN")
    mesaj: str  # Ä°nsan iÃ§in aÃ§Ä±klama
    skor: float  # Bu uyarÄ±nÄ±n risk puanÄ±na katkÄ±sÄ±

    def __str__(self) -> str:
        return f"[Guardrail:{self.kod}] {self.mesaj}"


# â”€â”€ Hallucination filtresi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


class HallucinationFiltresi:
    """LLM yanÄ±tÄ±nda hallucination iÅŸaretlerini tespit eder.

    YanÄ±tÄ± deÄŸiÅŸtirmez â€” uyarÄ± listesi Ã¼retir ve yanÄ±tÄ± olduÄŸu gibi dÃ¶ndÃ¼rÃ¼r.
    ReAct dÃ¶ngÃ¼sÃ¼ veya kullanÄ±cÄ± uyarÄ±larÄ± gÃ¶z Ã¶nÃ¼nde bulundurarak karar verebilir.

    Args:
        esik_skor: Toplam risk puanÄ± bu eÅŸiÄŸi geÃ§erse yanÄ±t "riskli" sayÄ±lÄ±r.
                   VarsayÄ±lan: 2.0
    """

    def __init__(self, esik_skor: float = 2.0) -> None:
        if esik_skor <= 0:
            raise ValueError(f"esik_skor pozitif olmalÄ±, alÄ±nan: {esik_skor}")
        self.esik_skor = esik_skor
        self._toplam_kontrol: int = 0
        self._uyarili_yanit: int = 0

    # â”€â”€ Ana API â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def filtrele(
        self,
        yanit: str,
        hedef: str = "",
    ) -> tuple[str, list[Uyari]]:
        """YanÄ±tÄ± hallucination iÃ§in tara.

        Args:
            yanit:  LLM'den gelen ham metin.
            hedef:  KullanÄ±cÄ± gÃ¶revinin kÄ±sa aÃ§Ä±klamasÄ± (iliÅŸki kontrolÃ¼ iÃ§in).

        Returns:
            (degistirilmemis_yanit, uyari_listesi)
            UyarÄ± listesi boÅŸsa yanÄ±t temiz kabul edilir.
        """
        self._toplam_kontrol += 1
        uyarilar: list[Uyari] = []

        uyarilar.extend(self._emin_olmayan_kontrol(yanit))
        uyarilar.extend(self._kesin_iddia_kontrol(yanit))
        uyarilar.extend(self._yanlis_surum_kontrol(yanit))
        uyarilar.extend(self._oz_referans_kontrol(yanit))
        uyarilar.extend(self._uzun_yanit_kontrol(yanit))
        uyarilar.extend(self._iliski_kontrol(yanit, hedef))

        toplam_skor = sum(u.skor for u in uyarilar)
        if toplam_skor > self.esik_skor:
            self._uyarili_yanit += 1
            logger.debug(
                "[HallucinationFiltresi] Riskli yanÄ±t tespit edildi (skor=%.2f, eÅŸik=%.2f).",
                toplam_skor,
                self.esik_skor,
            )

        return yanit, uyarilar

    def istatistik(self) -> dict[str, float | int]:
        """Birikimli kontrol istatistiklerini dÃ¶ndÃ¼rÃ¼r."""
        return {
            "toplam_kontrol": self._toplam_kontrol,
            "uyarili": self._uyarili_yanit,
            "oran": round(self._uyarili_yanit / self._toplam_kontrol, 3)
            if self._toplam_kontrol
            else 0.0,
        }

    # â”€â”€ Kontrol yÃ¶ntemleri â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _emin_olmayan_kontrol(self, yanit: str) -> list[Uyari]:
        if _EMIN_OLMAYAN_RE.search(yanit):
            return [
                Uyari(
                    kod="EMIN_OLMAYAN",
                    mesaj="YanÄ±t belirsiz/emin olmayan dil iÃ§eriyor â€” doÄŸrulama Ã¶nerilir.",
                    skor=0.5,
                )
            ]
        return []

    def _kesin_iddia_kontrol(self, yanit: str) -> list[Uyari]:
        if _KESIN_IDDIA_RE.search(yanit):
            return [
                Uyari(
                    kod="KESIN_IDDIA",
                    mesaj="YanÄ±t doÄŸrulanamaz kesin iddia iÃ§eriyor.",
                    skor=1.0,
                )
            ]
        return []

    def _yanlis_surum_kontrol(self, yanit: str) -> list[Uyari]:
        m = _YANLIS_SURUM_RE.search(yanit)
        if m:
            return [
                Uyari(
                    kod="YANLIS_SURUM",
                    mesaj=f"Eski/yanlÄ±ÅŸ sÃ¼rÃ¼m referansÄ±: '{m.group()}'.",
                    skor=1.5,
                )
            ]
        return []

    def _oz_referans_kontrol(self, yanit: str) -> list[Uyari]:
        if _OZ_REFERANS_RE.search(yanit):
            return [
                Uyari(
                    kod="OZ_REFERANS",
                    mesaj="LLM internet/disk eriÅŸimi iddiasÄ± â€” muhtemel halÃ¼sinasyon.",
                    skor=2.0,
                )
            ]
        return []

    def _uzun_yanit_kontrol(self, yanit: str) -> list[Uyari]:
        if len(yanit) > _UZUN_YANIT_ESIGI:
            return [
                Uyari(
                    kod="UZUN_YANIT",
                    mesaj=f"YanÄ±t uzun ({len(yanit)} karakter) â€” baÅŸ/son kontrolÃ¼ Ã¶nerilir.",
                    skor=0.3,
                )
            ]
        return []

    def _iliski_kontrol(self, yanit: str, hedef: str) -> list[Uyari]:
        """Hedef kelimeleriyle yanÄ±t arasÄ±ndaki Ã¶rtÃ¼ÅŸmeyi basitÃ§e kontrol eder."""
        if len(hedef) <= 10 or len(yanit) <= 50:
            return []
        hedef_kelimeleri = set(hedef.lower().split()[:5])
        yanit_kelimeleri = set(yanit.lower().split())
        if hedef_kelimeleri and not hedef_kelimeleri & yanit_kelimeleri:
            return [
                Uyari(
                    kod="ILISKISIZ",
                    mesaj="YanÄ±t hedefe Ã§ok az atÄ±f iÃ§eriyor.",
                    skor=0.5,
                )
            ]
        return []


# â”€â”€ HITL SÄ±kÄ±laÅŸtÄ±rma â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

# VarsayÄ±lan ek riskli araÃ§lar
_EK_RISKLI_ARACLAR: frozenset[str] = frozenset(
    {
        "DOSYA_YAZ",  # Disk yazma
        "TARAYICI_AC",  # TarayÄ±cÄ± aÃ§ma
        "WEB_ARA",  # Ä°nternet eriÅŸimi
        "TELEGRAM_GONDER",  # DÄ±ÅŸ mesaj gÃ¶nderme
        "GORUNTU_ANALIZ",  # GÃ¶rÃ¼ntÃ¼ â†’ LLaVA
    }
)


class HITLSikistirici:
    """HITL onay eÅŸiÄŸini yÃ¼kseltip daha fazla aracÄ± onaya tabi tutan yÃ¶netici.

    motor.ekstra_riskli kÃ¼mesini geniÅŸleterek ek araÃ§larÄ± HITL akÄ±ÅŸÄ±na alÄ±r.
    geri_al() Ã§aÄŸrÄ±sÄ±yla orijinal kÃ¼me geri yÃ¼klenir.

    Args:
        motor:       ReAct motoru (calistir() metoduna sahip nesne).
        ek_araclar:  Onaya eklenecek araÃ§ adlarÄ± kÃ¼mesi.
                     None ise _EK_RISKLI_ARACLAR kullanÄ±lÄ±r.
    """

    def __init__(
        self,
        motor: Optional[object] = None,
        ek_araclar: Optional[frozenset[str]] = None,
    ) -> None:
        self._motor = motor
        self._ek_araclar: frozenset[str] = ek_araclar or _EK_RISKLI_ARACLAR
        self._orijinal_riskli: Optional[set[str]] = None
        self._aktif = False

    def sikilas(self) -> None:
        """RISKLI kÃ¼mesini geniÅŸlet ve HITL eÅŸiÄŸini yÃ¼kselt."""
        if self._aktif:
            logger.debug(
                "[HITL] Zaten sÄ±kÄ±laÅŸtÄ±rÄ±lmÄ±ÅŸ, tekrar Ã§aÄŸrÄ± gÃ¶rmezden gelindi."
            )
            return
        if not self._motor:
            logger.warning("[HITL] Motor tanÄ±mlÄ± deÄŸil; sÄ±kÄ±laÅŸtÄ±rma atlandÄ±.")
            return
        if not hasattr(self._motor, "calistir"):
            logger.warning("[HITL] Motor.calistir() yok; sÄ±kÄ±laÅŸtÄ±rma atlandÄ±.")
            return

        # ekstra_riskli attr'u yoksa boÅŸ kÃ¼meyle baÅŸlat
        if not hasattr(self._motor, "ekstra_riskli"):
            self._motor.ekstra_riskli = set()  # type: ignore[union-attr]

        self._orijinal_riskli = set(self._motor.ekstra_riskli)  # type: ignore[union-attr]
        self._motor.ekstra_riskli |= self._ek_araclar  # type: ignore[union-attr]
        self._aktif = True
        logger.info(
            "[HITL] SÄ±kÄ±laÅŸtÄ±rÄ±ldÄ±: %d araÃ§ onaya eklendi.", len(self._ek_araclar)
        )

    def geri_al(self) -> None:
        """RISKLI kÃ¼mesini eski haline getir."""
        if not self._aktif:
            return
        if self._motor and self._orijinal_riskli is not None:
            self._motor.ekstra_riskli = self._orijinal_riskli  # type: ignore[union-attr]
        self._aktif = False
        logger.info("[HITL] SÄ±kÄ±laÅŸtÄ±rma geri alÄ±ndÄ±.")

    @property
    def aktif(self) -> bool:
        """SÄ±kÄ±laÅŸtÄ±rma aktif mi?"""
        return self._aktif

    # Geriye dÃ¶nÃ¼k uyumluluk
    def aktif_mi(self) -> bool:  # noqa: D102
        return self._aktif


# â”€â”€ Motor HITL yamasÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def motor_hitl_yamasi_uygula(motor: object) -> None:
    """motor.calistir() metoduna ekstra_riskli desteÄŸi ekler (monkey-patch).

    Motor varsayÄ±lan olarak yalnÄ±zca sabit RISKLI kÃ¼mesine bakar.
    Bu yama, motor.ekstra_riskli kÃ¼mesini de kontrol etmesini saÄŸlar.
    Yama yalnÄ±zca bir kez uygulanÄ±r; tekrar Ã§aÄŸrÄ±lmasÄ± gÃ¼venlidir.

    Args:
        motor: calistir(arac, ham_param) metoduna sahip nesne.
    """
    if hasattr(motor, "_orijinal_calistir"):
        return  # Zaten uygulandÄ±

    motor._orijinal_calistir = motor.calistir  # type: ignore[union-attr]

    def _yamali_calistir(arac: str, ham_param: str) -> str:
        ekstra: frozenset[str] | set[str] = getattr(motor, "ekstra_riskli", frozenset())
        onay_fn = getattr(motor, "onay_fonksiyonu", None)

        if arac in ekstra and onay_fn is not None:
            ozet = ham_param[:120] if ham_param else ""
            if not onay_fn(arac, ozet):
                return f"[Ä°ptal]: KullanÄ±cÄ± '{arac}' eylemini reddetti (HITL)."

        return motor._orijinal_calistir(arac, ham_param)  # type: ignore[union-attr]

    motor.calistir = _yamali_calistir  # type: ignore[union-attr]
    logger.info("[HITL] Motor yamasÄ± uygulandÄ±.")


# â”€â”€ HÄ±zlÄ± test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

if __name__ == "__main__":
    import logging as _logging

    _logging.basicConfig(level=_logging.DEBUG, format="%(levelname)s %(message)s")

    print("=== Hallucination Filtresi Testi ===")
    filtre = HallucinationFiltresi(esik_skor=1.5)

    testler: list[tuple[str, str]] = [
        ("Python 2.7 ile test.py dosyasÄ±nÄ± yazacaÄŸÄ±m.", "Python ile dosya yaz"),
        ("DosyayÄ± oluÅŸturdum ve internet'ten kontrol ettim.", "dosya oluÅŸtur"),
        ("Bu iÅŸlevi Ã§aÄŸÄ±rabilirsin.", "fonksiyon Ã§aÄŸÄ±r"),
        ("Bu kesinlikle %100 Ã§alÄ±ÅŸacak.", "gÃ¼venilir kod"),
        ("Belki galiba bu yÃ¶ntem daha iyi olabilir.", "yÃ¶ntem seÃ§"),
    ]

    for yanit, hedef in testler:
        _, uyarilar = filtre.filtrele(yanit, hedef=hedef)
        etiket = "RÄ°SKLÄ°" if uyarilar else "TEMÄ°Z "
        print(f"[{etiket}] {yanit[:55]}")
        for u in uyarilar:
            print(f"         {u}")

    print(f"\nÄ°statistik: {filtre.istatistik()}")

    print("\n=== HITL Testi ===")
    hitl = HITLSikistirici()
    hitl.sikilas()
    print(f"Aktif mi: {hitl.aktif}")
    hitl.geri_al()
    print(f"Aktif mi: {hitl.aktif}")
