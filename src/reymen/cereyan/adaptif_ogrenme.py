# -*- coding: utf-8 -*-
"""
adaptif_ogrenme.py â€” Adaptive learning and self-correction module.

Two functions:
  1. User preferences: saves corrections like "no, do it this way".
     Saved preferences are injected into the system prompt in subsequent sessions.

  2. Self-correction: Python code test result + automatic correction loop API
     for use by the next module.

Usage::

    ao = AdaptifOgrenme()

    # Preference detection (used in main.py's ReAct loop)
    ao.kullanici_mesaji_isle("no, always write files with UTF-8")

    # System prompt injection
    tercihler = ao.tercih_blogu_al()

    # Python self-correction
    sonuc = ao.python_duzelt_ve_calistir(kod, motor, max_deneme=2)
"""

import json
import os
import re
import time
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.resolve()
TERCIH_DOSYASI = ROOT / ".ReYMeN" / "kullanici_tercihleri.json"
MAKS_TERCIH = 50  # En fazla bu kadar tercih saklanÄ±r

# KullanÄ±cÄ± düzeltme sinyalleri
_DUZELTME_SINYALLERI = [
    r"\bhay[Ä±i]r\b",
    r"\bdeÄŸil\b",
    r"\byapma\b",
    r"\bstop\b",
    r"\bher\s+zaman\b",
    r"\bhiç(?:bir\s+zaman)?\b",
    r"\bböyle\s+(?:yapma|yap)\b",
    r"\b(?:ÅŸöyle|bu\s+ÅŸekilde)\s+yap\b",
    r"\bkullanma\b",
    r"\bnot:\b",
    r"\bhatÄ±rl[ae]\b",
    r"\blütfen\s+(?:bir\s+daha)?\s*yapma\b",
    r"\bgeleceÄŸe\s+not\b",
]

_DUZELTME_RE = re.compile("|".join(_DUZELTME_SINYALLERI), re.IGNORECASE)


class AdaptifOgrenme:
    """Class that saves user preferences and provides self-correction."""

    def __init__(self, tercih_dosyasi: str = None):
        self._dosya = Path(tercih_dosyasi) if tercih_dosyasi else TERCIH_DOSYASI
        self._dosya.parent.mkdir(parents=True, exist_ok=True)
        self._tercihler: list = self._yukle()

    # â”€â”€ Tercih yönetimi â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _yukle(self) -> list:
        if self._dosya.exists():
            try:
                return json.loads(self._dosya.read_text(encoding="utf-8"))
            except Exception as _e:
                logger.warning("[AdaptifOgrenme] except Exception (L70): %s", Exception)
                pass
        return []

    def _kaydet(self):
        try:
            self._dosya.write_text(
                json.dumps(self._tercihler, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            print(f"[Adaptif]: Tercih kaydetme hatasÄ±: {e}")

    def tercih_ekle(self, metin: str, kaynak: str = "kullanici") -> bool:
        """Add a new preference. Does not add if the same text already exists.

        Returns:
            True: added, False: already exists
        """
        metin = metin.strip()[:300]
        if not metin:
            return False
        mevcut_metinler = {t["metin"] for t in self._tercihler}
        if metin in mevcut_metinler:
            return False
        self._tercihler.append(
            {
                "metin": metin,
                "kaynak": kaynak,
                "zaman": time.strftime("%Y-%m-%d %H:%M"),
            }
        )
        # Kapasite sÄ±nÄ±rÄ±
        if len(self._tercihler) > MAKS_TERCIH:
            self._tercihler = self._tercihler[-MAKS_TERCIH:]
        self._kaydet()
        print(f"[Adaptif]: Tercih kaydedildi -> {metin[:60]}")
        return True

    def kullanici_mesaji_isle(self, mesaj: str) -> bool:
        """Convert a user message to a preference if it contains a correction signal.

        Returns:
            True: correction signal found and saved
        """
        if _DUZELTME_RE.search(mesaj):
            return self.tercih_ekle(mesaj, kaynak="kullanici_duzeltme")
        return False

    def tercih_blogu_al(self, limit: int = 10) -> str:
        """Return the last N preferences in a format suitable for system prompt injection."""
        if not self._tercihler:
            return ""
        son = self._tercihler[-limit:]
        satirlar = "\n".join(f"- {t['metin']}" for t in son)
        return f"\n== KULLANICI TERCÄ°HLERÄ° (bunlara uy) ==\n{satirlar}\n"

    def tercih_sayisi(self) -> int:
        return len(self._tercihler)

    def tum_tercihler(self) -> list:
        return list(self._tercihler)

    def tercih_sil(self, indeks: int) -> bool:
        if 0 <= indeks < len(self._tercihler):
            silinen = self._tercihler.pop(indeks)
            self._kaydet()
            print(f"[Adaptif]: Tercih silindi: {silinen['metin'][:50]}")
            return True
        return False

    def tercihleri_temizle(self):
        self._tercihler.clear()
        self._kaydet()

    # â”€â”€ Self-correction â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def python_duzelt_ve_calistir(
        self,
        kod: str,
        motor,
        provider=None,
        max_deneme: int = 2,
    ) -> str:
        """Run Python code, fix errors with LLM and retry.

        Args:
            kod:        Python code to execute.
            motor:      Motor instance (for PYTHON_CALISTIR).
            provider:   LLM provider (Beyin instance). None returns just the error.
            max_deneme: Maximum number of correction attempts.

        Returns:
            Output of the running code or the final error message.
        """
        mevcut_kod = kod
        son_hata = ""

        for deneme in range(max_deneme + 1):
            sonuc = motor.calistir("PYTHON_CALISTIR", f'"{mevcut_kod}"')
            if (
                "[Hata]" not in sonuc
                and "Error" not in sonuc
                and "Traceback" not in sonuc
            ):
                if deneme > 0:
                    print(f"[Self-correction]: {deneme}. denemede düzeldi.")
                return sonuc

            son_hata = sonuc
            if deneme >= max_deneme or provider is None:
                break

            # LLM'den düzeltme iste
            duzeltme_promptu = (
                f"AÅŸaÄŸÄ±daki Python kodu ÅŸu hatayÄ± verdi:\n\n"
                f"KOD:\n```python\n{mevcut_kod}\n```\n\n"
                f"HATA:\n{son_hata[:500]}\n\n"
                f"Kodu düzelt ve SADECE düzeltilmiÅŸ kodu yaz. AçÄ±klama ekleme."
            )
            try:
                yanit = provider.uret(
                    "Sen bir Python kod düzeltici asistanÄ±sÄ±n.",
                    [{"role": "user", "content": duzeltme_promptu}],
                )
                # Kod bloÄŸunu çÄ±kar
                m = re.search(r"```(?:python)?\s*\n(.+?)```", yanit, re.DOTALL)
                if m:
                    mevcut_kod = m.group(1).strip()
                else:
                    mevcut_kod = yanit.strip()
                print(f"[Self-correction]: Deneme {deneme + 1}, kod düzeltildi.")
            except Exception as e:
                print(f"[Self-correction]: LLM hatasÄ±: {e}")
                break

        return f"[Self-correction]: {max_deneme} denemede düzeltilemedi.\nSon hata: {son_hata[:300]}"


# â”€â”€ Motor entegrasyon yardÄ±mcÄ±sÄ± â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€


def adaptif_ogrenme_sistemi_kur() -> AdaptifOgrenme:
    """Create a global AdaptifOgrenme instance."""
    return AdaptifOgrenme()


if __name__ == "__main__":
    ao = AdaptifOgrenme()

    # Düzeltme tespiti testi
    testler = [
        "hayÄ±r, her zaman UTF-8 kullan",
        "tamam harika",
        "bunu bir daha yapma lütfen",
        "dosya oluÅŸtur",
        "hatÄ±rla: API key'i asla yazdÄ±rma",
    ]
    print("=== Düzeltme Tespiti ===")
    for t in testler:
        tespit = ao.kullanici_mesaji_isle(t)
        print(f"{'[KAYDEDILDI]' if tespit else '[normal]  '} {t}")

    print(f"\nToplam tercih: {ao.tercih_sayisi()}")
    print(ao.tercih_blogu_al())
