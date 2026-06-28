# -*- coding: utf-8 -*-
"""base64_tool.py — Base64 encode/decode aracı.

Metin veya dosyayı base64 ile encode/decode eder.
"""

import json
import base64
from pathlib import Path


TOOL_META = {
    "aciklama": "Metin veya dosyayı Base64 ile encode/decode eder.",
    "parametreler": [
        {"ad": "veri", "tip": "str", "aciklama": "Encode/decode edilecek veri. 'd:' ile başlarsa dosya yolu."},
        {"ad": "islem", "tip": "str", "aciklama": "'encode' (varsayılan) veya 'decode'."},
    ],
    "ornek": 'BASE64_TOOL("Merhaba Dünya", islem="encode")',
    "kategori": "conversion",
}


def run(veri: str = "", islem: str = "encode", *args, **kwargs) -> str:
    """Base64 encode/decode yap.

    Args:
        veri: İşlenecek veri. 'd:' ile başlarsa dosya yolu.
        islem: 'encode' (varsayılan) veya 'decode'.

    Returns:
        JSON: işlem sonucu.
    """
    if not veri:
        return json.dumps({"hata": "veri parametresi zorunludur."}, ensure_ascii=False)

    try:
        # Dosyadan oku
        if veri.startswith("d:") or veri.startswith("D:"):
            dosya_yolu = veri[2:].strip()
            yol = Path(dosya_yolu)
            if not yol.exists():
                return json.dumps({"hata": f"Dosya bulunamadi: {dosya_yolu}"}, ensure_ascii=False)
            raw_bytes = yol.read_bytes()
            kaynak = f"dosya: {dosya_yolu}"
        else:
            if islem == "encode":
                raw_bytes = veri.encode("utf-8")
            else:
                raw_bytes = veri.encode("utf-8")
            kaynak = "metin"

        if islem == "encode":
            sonuc = base64.b64encode(raw_bytes).decode("utf-8")
            return json.dumps({
                "islem": "encode",
                "kaynak": kaynak,
                "sonuc": sonuc,
                "giris_boyutu": len(raw_bytes),
                "cikti_boyutu": len(sonuc),
            }, ensure_ascii=False, indent=2)
        elif islem == "decode":
            try:
                decoded = base64.b64decode(veri)
                # UTF-8'e çevirmeyi dene
                try:
                    metin = decoded.decode("utf-8")
                    return json.dumps({
                        "islem": "decode",
                        "sonuc": metin,
                        "cikti_boyutu": len(decoded),
                    }, ensure_ascii=False, indent=2)
                except UnicodeDecodeError:
                    return json.dumps({
                        "islem": "decode",
                        "sonuc": repr(decoded),
                        "cikti_boyutu": len(decoded),
                        "not": "Binary veri, UTF-8 olarak decode edilemedi.",
                    }, ensure_ascii=False, indent=2)
            except base64.binascii.Error as e:
                return json.dumps({
                    "hata": f"Base64 decode hatasi: {str(e)}"
                }, ensure_ascii=False)
        else:
            return json.dumps({"hata": f"Geçersiz işlem: {islem}. 'encode' veya 'decode' kullanın."}, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== ENCODE ===")
    print(run("Merhaba Dünya", islem="encode"))

    print("\n=== DECODE ===")
    encoded = base64.b64encode("Merhaba Dünya".encode("utf-8")).decode("utf-8")
    print(run(encoded, islem="decode"))
