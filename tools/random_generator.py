# -*- coding: utf-8 -*-
"""random_generator.py — Rastgele veri üretme aracı.

Rastgele sayı, string, UUID, şifre, renk kodu üretir.
"""

import json
import random
import string
import uuid
import time


TOOL_META = {
    "aciklama": "Rastgele veri üretir: sayı, string, UUID, şifre, renk kodu, tarih.",
    "parametreler": [
        {"ad": "tur", "tip": "str", "aciklama": "Veri türü: sayi, string, uuid, sifre, renk, tarih, secim."},
        {"ad": "parametreler", "tip": "str", "aciklama": "Türe göre parametreler JSON olarak (örn: '{\"min\":1,\"max\":100}')."},
    ],
    "ornek": 'RANDOM_GENERATOR(tur="sifre", parametreler=\'{"uzunluk":16}\')',
    "kategori": "utility",
}


def run(tur: str = "uuid", parametreler: str = "{}", *args, **kwargs) -> str:
    """Rastgele veri üret.

    Args:
        tur: Veri türü (sayi, string, uuid, sifre, renk, tarih, secim).
        parametreler: JSON string olarak parametreler.

    Returns:
        JSON: üretilen veri.
    """
    if not tur:
        return json.dumps({"hata": "tur parametresi zorunludur."}, ensure_ascii=False)

    # Parametreleri parse et
    try:
        params = json.loads(parametreler) if parametreler else {}
    except json.JSONDecodeError as e:
        return json.dumps({"hata": f"Gecersiz parametre JSON: {str(e)}"}, ensure_ascii=False)

    tur = tur.lower()

    try:
        if tur == "sayi":
            min_v = params.get("min", 0)
            max_v = params.get("max", 100)
            adet = params.get("adet", 1)
            if adet > 1000:
                adet = 1000
            sayilar = [random.randint(min_v, max_v) for _ in range(adet)]
            return json.dumps({
                "tur": "sayi",
                "aralik": f"{min_v}-{max_v}",
                "adet": adet,
                "sonuc": sayilar if adet > 1 else sayilar[0],
            }, ensure_ascii=False, indent=2)

        elif tur == "string":
            uzunluk = params.get("uzunluk", 8)
            if uzunluk > 10000:
                uzunluk = 10000
            harfler = string.ascii_letters + string.digits
            sonuc = ''.join(random.choice(harfler) for _ in range(uzunluk))
            return json.dumps({
                "tur": "string",
                "uzunluk": uzunluk,
                "sonuc": sonuc,
            }, ensure_ascii=False, indent=2)

        elif tur == "uuid":
            adet = params.get("adet", 1)
            if adet > 100:
                adet = 100
            uuids = [str(uuid.uuid4()) for _ in range(adet)]
            return json.dumps({
                "tur": "uuid",
                "adet": adet,
                "sonuc": uuids if adet > 1 else uuids[0],
            }, ensure_ascii=False, indent=2)

        elif tur == "sifre":
            uzunluk = params.get("uzunluk", 12)
            if uzunluk < 4:
                uzunluk = 4
            if uzunluk > 128:
                uzunluk = 128
            buyuk_harf = params.get("buyuk_harf", True)
            kucuk_harf = params.get("kucuk_harf", True)
            rakam = params.get("rakam", True)
            ozel = params.get("ozel", True)

            havuz = ""
            if kucuk_harf:
                havuz += string.ascii_lowercase
            if buyuk_harf:
                havuz += string.ascii_uppercase
            if rakam:
                havuz += string.digits
            if ozel:
                havuz += "!@#$%^&*()_+-=[]{}|;:,.<>?"

            if not havuz:
                havuz = string.ascii_letters + string.digits

            # En az bir karakterden garanti
            sifre = []
            if buyuk_harf:
                sifre.append(random.choice(string.ascii_uppercase))
            if kucuk_harf:
                sifre.append(random.choice(string.ascii_lowercase))
            if rakam:
                sifre.append(random.choice(string.digits))
            if ozel:
                sifre.append(random.choice("!@#$%"))

            kalan = uzunluk - len(sifre)
            if kalan > 0:
                sifre.extend(random.choice(havuz) for _ in range(kalan))
            random.shuffle(sifre)

            return json.dumps({
                "tur": "sifre",
                "uzunluk": uzunluk,
                "guclu": uzunluk >= 12 and buyuk_harf and kucuk_harf and rakam and ozel,
                "sonuc": ''.join(sifre),
            }, ensure_ascii=False, indent=2)

        elif tur == "renk":
            format_tip = params.get("format", "hex")
            if format_tip == "hex":
                renk = f"#{random.randint(0, 0xFFFFFF):06x}"
                r, g, b = int(renk[1:3], 16), int(renk[3:5], 16), int(renk[5:7], 16)
                return json.dumps({
                    "tur": "renk",
                    "format": "hex",
                    "sonuc": renk,
                    "rgb": [r, g, b],
                }, ensure_ascii=False, indent=2)
            elif format_tip == "rgb":
                r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                return json.dumps({
                    "tur": "renk",
                    "format": "rgb",
                    "sonuc": f"rgb({r},{g},{b})",
                    "hex": f"#{r:02x}{g:02x}{b:02x}",
                }, ensure_ascii=False, indent=2)
            else:
                return json.dumps({"hata": f"Geçersiz renk formatı: {format_tip}"}, ensure_ascii=False)

        elif tur == "tarih":
            import datetime
            baslangic = params.get("baslangic", "2020-01-01")
            bitis = params.get("bitis", "2030-12-31")
            try:
                bas = datetime.datetime.strptime(baslangic, "%Y-%m-%d")
                bit = datetime.datetime.strptime(bitis, "%Y-%m-%d")
            except ValueError as e:
                return json.dumps({"hata": f"Tarih format hatasi (YYYY-AA-GG): {str(e)}"}, ensure_ascii=False)

            fark = (bit - bas).days
            rastgele_gun = random.randint(0, max(0, fark))
            rastgele_tarih = bas + datetime.timedelta(days=rastgele_gun)

            return json.dumps({
                "tur": "tarih",
                "sonuc": rastgele_tarih.strftime("%Y-%m-%d"),
                "gun_adi": rastgele_tarih.strftime("%A"),
            }, ensure_ascii=False, indent=2)

        elif tur == "secim":
            secenekler = params.get("secenekler", [])
            if not secenekler or not isinstance(secenekler, list):
                return json.dumps({"hata": "secenekler parametresi liste olarak gerekli (orn: [\"a\",\"b\",\"c\"])"}, ensure_ascii=False)
            adet = params.get("adet", 1)
            if adet > len(secenekler):
                adet = len(secenekler)
            secilen = random.sample(secenekler, adet) if adet > 0 else []
            return json.dumps({
                "tur": "secim",
                "adet": adet,
                "sonuc": secilen if adet > 1 else (secilen[0] if secilen else None),
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({
                "hata": f"Geçersiz tür: {tur}",
                "desteklenen": ["sayi", "string", "uuid", "sifre", "renk", "tarih", "secim"],
            }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== UUID ===")
    print(run("uuid"))

    print("\n=== SAYI ===")
    print(run("sayi", '{"min":1,"max":100,"adet":5}'))

    print("\n=== SIFRE ===")
    print(run("sifre", '{"uzunluk":16}'))

    print("\n=== RENK ===")
    print(run("renk", '{"format":"hex"}'))

    print("\n=== SECIM ===")
    print(run("secim", '{"secenekler":["elma","armut","muz","cilek"],"adet":2}'))
