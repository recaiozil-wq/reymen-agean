"""
Patch/V4A format ayrıştırıcı.
*** Begin/End Patch formatını parse eder.
"""
import re
import os

PATCH_PATTERN = re.compile(
    r'\*\*\*\s*Begin\s*Patch\s*\*\*\*\s*'
    r'(.*?)'
    r'\*\*\*\s*End\s*Patch\s*\*\*\*\s*',
    re.DOTALL
)

UPDATE_FILE_PATTERN = re.compile(r'\*\*\*\s*Update\s*File:\s*(.+?)\s*\*\*\*')


def _parse_patch(patch_metni):
    """Patch metnini parse et."""
    if not patch_metni:
        return None, "Patch metni boş."

    bloklar = []
    for match in PATCH_PATTERN.finditer(patch_metni):
        blok = match.group(1).strip()
        dosya_eslesme = UPDATE_FILE_PATTERN.search(blok)
        dosya_yolu = dosya_eslesme.group(1).strip() if dosya_eslesme else None

        # Dosya yolundan sonraki içerik
        icerik = blok
        if dosya_eslesme:
            idx = dosya_eslesme.end()
            icerik = blok[idx:].strip()

        bloklar.append({
            'dosya': dosya_yolu,
            'icerik': icerik
        })

    if not bloklar:
        return None, "Geçerli patch bloğu bulunamadı."

    return bloklar, None


def run(islem='parse', patch_metni=None, **kwargs):
    """
    Patch/V4A format ayrıştırıcı.

    Parametreler:
        islem (str): 'parse', 'dogrula' veya 'uygula'
        patch_metni (str): *** Begin/End Patch formatında metin

    Returns:
        str: İşlem sonucu.
    """
    try:
        if not patch_metni:
            return "Hata: 'patch_metni' parametresi zorunludur."

        bloklar, hata = _parse_patch(patch_metni)

        if hata:
            return f"Parse hatası: {hata}"

        if islem == 'parse':
            import json
            return json.dumps(bloklar, indent=2, ensure_ascii=False)

        elif islem == 'dogrula':
            sorunlar = []
            for i, blok in enumerate(bloklar):
                if not blok['dosya']:
                    sorunlar.append(f"Blok {i + 1}: Dosya yolu belirtilmemiş.")
                if not blok['icerik']:
                    sorunlar.append(f"Blok {i + 1}: İçerik boş.")
                if not blok['icerik'].startswith('@@'):
                    sorunlar.append(f"Blok {i + 1}: İçerik @@ ile başlamalı.")
            if sorunlar:
                return "Doğrulama sorunları:\n" + "\n".join(sorunlar)
            return f"Patch geçerli ({len(bloklar)} blok)."

        elif islem == 'uygula':
            sonuclar = []
            for i, blok in enumerate(bloklar):
                if not blok['dosya']:
                    sonuclar.append(f"Blok {i + 1}: Dosya yolu eksik, atlandı.")
                    continue
                sonuclar.append(f"Blok {i + 1}: '{blok['dosya']}' -> uygulanacak ({len(blok['icerik'])} karakter)")
            return "Patch uygulama sonuçları:\n" + "\n".join(sonuclar)

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'parse', 'dogrula' veya 'uygula' kullanın."

    except Exception as e:
        return f"Patch parser hatası: {str(e)}"
