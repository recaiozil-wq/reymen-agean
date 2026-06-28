# -*- coding: utf-8 -*-
"""tools/macro.py — Makro Oynatma Araci.

Kaydedilmis makrolari oynatir.
"""

from pathlib import Path

MAKRO_KLASOR = Path(__file__).parent.parent / ".ReYMeN" / "makrolar"


def oynat(makro_adi: str) -> str:
    """Bir makroyu oynat.

    Args:
        makro_adi: Makro adi (dosya adi, .py olmadan)

    Returns:
        Durum mesaji
    """
    if not makro_adi:
        return "[Makro]: Makro adi gerekli."

    makro_dosyasi = MAKRO_KLASOR / f"{makro_adi}.py"
    if not makro_dosyasi.exists():
        # Uzantısız dene
        for f in MAKRO_KLASOR.glob(f"{makro_adi}*"):
            makro_dosyasi = f
            break
        if not makro_dosyasi.exists():
            return f"[Makro]: '{makro_adi}' bulunamadi. Mevcut: {[f.stem for f in MAKRO_KLASOR.glob('*.py')]}"

    try:
        import importlib.util, sys
        spec = importlib.util.spec_from_file_location("_makro", makro_dosyasi)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules["_makro"] = mod
            spec.loader.exec_module(mod)
            if hasattr(mod, "ADIMLAR"):
                adimlar = mod.ADIMLAR
                from motor import Motor
                m = Motor()
                sonuc = []
                for adim in adimlar:
                    arac = adim.get("eylem", "")
                    param = adim.get("parametre", "")
                    bekle = adim.get("bekle", 0)
                    import time
                    gozlem = m.calistir(arac, f'"{param}"')
                    sonuc.append(f"{arac}: {gozlem[:60]}")
                    if bekle:
                        time.sleep(bekle)
                return "[Makro] Oynatildi:\n" + "\n".join(sonuc)
            return f"[Makro]: {makro_adi} icinde ADIMLAR bulunamadi."
        return "[Makro]: Dosya yuklenemedi."
    except Exception as e:
        return f"[Makro]: Hata: {e}"


def ping() -> bool:
    return MAKRO_KLASOR.exists() and any(MAKRO_KLASOR.glob("*.py"))


if __name__ == "__main__":
    print(oynat("ornek_makro"))
