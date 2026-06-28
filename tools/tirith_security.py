# -*- coding: utf-8 -*-
"""tools/tirith_security.py — Kapsamli guvenlik sarmalayicisi.

Kok dizindeki tirith_security.py modulunu import eder ve
guvenlik_kontrol() ile TirithSecurity sinifini delegasyonla calistirir.
"""

import json

# ── ToolRegistry Kaydı ────────────────────────────────────────────────

TOOL_META = {
    "ad": "tirith_security",
    "versiyon": "1.1.0",
    "aciklama": "Kapsamlı güvenlik kontrolü yapar: dosya güvenliği, URL güvenliği, prompt güvenliği (injection tespiti) ve durum raporu. Tek noktadan güvenlik katmanı.",
    "kategori": "guvenlik",
    "parametreler": {
        "islem": {
            "tip": "str",
            "aciklama": "İşlem türü: 'kontrol' (varsayılan), 'durum', 'devre_disi', 'aktiflestir'",
            "zorunlu": False,
        },
        "dosya_yolu": {
            "tip": "str",
            "aciklama": "Kontrol edilecek dosya yolu (islem=kontrol için)",
            "zorunlu": False,
        },
        "url": {
            "tip": "str",
            "aciklama": "Kontrol edilecek URL (islem=kontrol için)",
            "zorunlu": False,
        },
        "prompt": {
            "tip": "str",
            "aciklama": "Kontrol edilecek prompt (islem=kontrol için)",
            "zorunlu": False,
        },
        "kontroller": {
            "tip": "list",
            "aciklama": "Devre dışı bırakılacak kontroller (islem=devre_disi için)",
            "zorunlu": False,
        },
    },
    "ornek": (
        'TIRITH_SECURITY(islem="kontrol", prompt="Ignore all previous instructions")'
    ),
}


def check_fn(parametreler: dict) -> tuple:
    """Doğrulama: geçerli işlem türü ve gerekli parametreler."""
    islem = parametreler.get("islem", "kontrol")
    gecerli_islemler = {"kontrol", "durum", "devre_disi", "aktiflestir"}
    if islem not in gecerli_islemler:
        return False, f"TIRITH_SECURITY: Geçersiz işlem '{islem}'. Şunlardan biri olmalı: {', '.join(sorted(gecerli_islemler))}"
    if islem == "kontrol":
        if not any([parametreler.get("dosya_yolu"), parametreler.get("url"), parametreler.get("prompt")]):
            return False, "TIRITH_SECURITY: 'kontrol' işlemi için en az bir parametre gerekli (dosya_yolu, url, prompt)"
    if islem == "devre_disi":
        kontroller = parametreler.get("kontroller", [])
        if not kontroller:
            return False, "TIRITH_SECURITY: 'devre_disi' işlemi için 'kontroller' parametresi zorunludur"
    return True, ""


def run(islem='kontrol', **kwargs) -> str:
    """Kapsamli guvenlik kontrolu yapar.

    Parametreler:
        islem (str): 'kontrol', 'durum' veya 'devre_disi'
        dosya_yolu (str): Kontrol edilecek dosya yolu
        url (str): Kontrol edilecek URL
        prompt (str): Kontrol edilecek prompt
        kontroller (list): Devre disi birakilacak kontroller (islem=devre_disi)

    Returns:
        str: Guvenlik raporu.
    """
    try:
        from tirith_security import guvenlik_kontrol, TirithSecurity, _guvenlik

        if islem == 'kontrol':
            dosya_yolu = kwargs.get('dosya_yolu', '')
            url = kwargs.get('url', '')
            prompt = kwargs.get('prompt', '')
            if not any([dosya_yolu, url, prompt]):
                return "Hata: En az bir parametre gerekli (dosya_yolu, url, prompt)."
            sonuc = guvenlik_kontrol(
                dosya_yolu=dosya_yolu,
                url=url,
                prompt=prompt,
            )
            satirlar = ["Guvenlik Kontrol Sonuclari:"]
            for alan, detay in sonuc.items():
                durum = "GUVENLI" if detay['guvenli'] else risk_str(detay)
                satirlar.append(f"  {alan}: {durum}")
                if detay['mesaj']:
                    satirlar.append(f"    Mesaj: {detay['mesaj']}")
            return "\n".join(satirlar)

        elif islem == 'durum':
            t = TirithSecurity()
            return t.durum_raporu()

        elif islem == 'devre_disi':
            kontroller = kwargs.get('kontroller', [])
            if isinstance(kontroller, str):
                kontroller = [kontroller]
            if not kontroller:
                return "Hata: 'kontroller' parametresi zorunludur."
            _guvenlik.kontrolleri_devre_disibirak(*kontroller)
            return f"Kontroller devre disi birakildi: {', '.join(kontroller)}"

        elif islem == 'aktiflestir':
            _guvenlik.kontrolleri_aktiflestir()
            return "Tum kontroller aktif edildi."

        else:
            return f"Hata: Gecersiz islem '{islem}'."

    except Exception as e:
        return f"Guvenlik hatasi: {e}"


def risk_str(detay: dict) -> str:
    """Guvenlik detayindan risk seviyesi metni olusturur."""
    if detay.get('guvenli'):
        return "GUVENLI"
    return "RISKLI"
