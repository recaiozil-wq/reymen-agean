# -*- coding: utf-8 -*-
"""clarify_tool.py — Netleştirme Aracı (Clarify).

ReYMeN'teki clarify tool'un ReYMeN uyarlaması.
Kullanıcının net olmayan taleplerinde geri sorar,
seçenek sunar veya açıklama ister.

ToolRegistry'e kayıt için:
    TOOL_META = {...}
    def run(...)
"""

TOOL_META = {
    "ad": "clarify",
    "versiyon": "1.0.0",
    "aciklama": "Net olmayan taleplerde kullanıcıya seçenek sunar veya açıklama ister.",
    "kategori": "orkestrasyon",
    "parametreler": {
        "soru": {
            "tip": "str",
            "aciklama": "Kullanıcıya sorulacak soru",
            "zorunlu": True,
        },
        "secenekler": {
            "tip": "list",
            "aciklama": "Sunulacak seçenek listesi (opsiyonel)",
            "zorunlu": False,
        },
        "varsayilan": {
            "tip": "str",
            "aciklama": "Kullanıcı cevap vermezse kullanılacak varsayılan",
            "zorunlu": False,
        },
    },
    "ornek": (
        'CLARIFY(soru="Hangi ortamda çalıştırayım?", '
        'secenekler=["local", "docker", "ssh"], varsayilan="local")'
    ),
}


def run(soru: str, secenekler: list = None, varsayilan: str = "") -> str:
    """Net olmayan taleplerde kullanıcıya soru sor.

    Args:
        soru: Kullanıcıya sorulacak soru metni
        secenekler: Sunulacak seçenek listesi (opsiyonel)
        varsayilan: Kullanıcı cevap vermezse kullanılacak değer

    Returns:
        str: Kullanıcının cevabı veya varsayılan değer
    """
    try:
        # Soruyu formatla
        if secenekler:
            secenek_metni = "\n".join(
                f"  {i + 1}. {s}" for i, s in enumerate(secenekler)
            )
            iletisim = (
                f"⚠️ **NETLEŞTİRME GEREKİYOR**\n\n"
                f"{soru}\n\n"
                f"Seçenekler:\n{secenek_metni}"
            )
            if varsayilan:
                iletisim += f"\n\n(Varsayılan: {varsayilan} — cevapsız geçer)"
        else:
            iletisim = (
                f"⚠️ **NETLEŞTİRME GEREKİYOR**\n\n"
                f"{soru}"
            )

        return f"[NETLESTIR] {iletisim}"

    except Exception as e:
        return f"[CLARIFY_HATASI: {e}]"


def check_fn(parametreler: dict) -> tuple:
    """Doğrulama: soru parametresi zorunlu."""
    if not parametreler.get("soru"):
        return False, "CLARIFY: 'soru' parametresi zorunludur"
    return True, ""


# Kısa kullanım alias
CLARIFY = run
