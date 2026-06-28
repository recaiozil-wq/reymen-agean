# -*- coding: utf-8 -*-
"""hash_tool.py — Hash hesaplama aracı.

Metin veya dosyanın MD5, SHA-1, SHA-256, SHA-512 hash'ini hesaplar.
"""

import json
import hashlib
from pathlib import Path


TOOL_META = {
    "aciklama": "Metin veya dosyanın MD5, SHA-1, SHA-256, SHA-512 hash'ini hesaplar.",
    "parametreler": [
        {"ad": "veri", "tip": "str", "aciklama": "Hashlenecek veri. 'd:' ile başlarsa dosya yolu."},
        {"ad": "algoritma", "tip": "str", "aciklama": "Hash algoritması: md5, sha1, sha256 (varsayılan), sha512."},
    ],
    "ornek": 'HASH_TOOL("Merhaba", algoritma="sha256")',
    "kategori": "conversion",
}


def run(veri: str = "", algoritma: str = "sha256", *args, **kwargs) -> str:
    """Hash hesapla.

    Args:
        veri: Hashlenecek veri. 'd:' ile başlarsa dosya yolu.
        algoritma: Hash algoritması (md5, sha1, sha256, sha512).

    Returns:
        JSON: hash değeri ve detaylar.
    """
    if not veri:
        return json.dumps({"hata": "veri parametresi zorunludur."}, ensure_ascii=False)

    algoritma = algoritma.lower()
    desteklenen = {"md5", "sha1", "sha256", "sha384", "sha512", "blake2b", "blake2s"}

    if algoritma not in desteklenen:
        return json.dumps({
            "hata": f"Geçersiz algoritma: {algoritma}. Desteklenenler: {', '.join(sorted(desteklenen))}"
        }, ensure_ascii=False)

    try:
        h = hashlib.new(algoritma)

        # Dosyadan oku
        if veri.startswith("d:") or veri.startswith("D:"):
            dosya_yolu = veri[2:].strip()
            yol = Path(dosya_yolu)
            if not yol.exists():
                return json.dumps({"hata": f"Dosya bulunamadi: {dosya_yolu}"}, ensure_ascii=False)

            # Büyük dosyalar için parça parça oku
            boyut = yol.stat().st_size
            with open(yol, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    h.update(chunk)

            return json.dumps({
                "algoritma": algoritma,
                "kaynak": f"dosya: {dosya_yolu}",
                "dosya_boyutu": boyut,
                "hash": h.hexdigest(),
            }, ensure_ascii=False, indent=2)
        else:
            h.update(veri.encode("utf-8"))
            return json.dumps({
                "algoritma": algoritma,
                "kaynak": "metin",
                "giris_boyutu": len(veri),
                "hash": h.hexdigest(),
            }, ensure_ascii=False, indent=2)

    except ValueError as e:
        return json.dumps({"hata": f"Geçersiz algoritma: {str(e)}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== SHA256 ===")
    print(run("Merhaba Dünya", algoritma="sha256"))

    print("\n=== MD5 ===")
    print(run("Merhaba Dünya", algoritma="md5"))

    print("\n=== SHA512 ===")
    print(run("Merhaba Dünya", algoritma="sha512"))
