# -*- coding: utf-8 -*-
"""date_tool.py — Tarih/saat biçimlendirme ve hesaplama aracı.

Tarih formatlama, fark hesaplama, zaman ekleme/çıkarma işlemleri yapar.
"""

import json
from datetime import datetime, timedelta, date


TOOL_META = {
    "aciklama": "Tarih/saat işlemleri: formatlama, fark hesaplama, zaman ekleme/çıkarma.",
    "parametreler": [
        {"ad": "islem", "tip": "str", "aciklama": "İşlem: simdi, formatla, fark, ekle, yilbasi, gun_bilgisi."},
        {"ad": "tarih1", "tip": "str", "aciklama": "Birinci tarih (YYYY-AA-GG veya ISO formatı)."},
        {"ad": "tarih2", "tip": "str", "aciklama": "İkinci tarih (fark hesabı için)."},
        {"ad": "hedef_format", "tip": "str", "aciklama": "Hedef format (örn: '%d.%m.%Y %H:%M')."},
        {"ad": "gun_sayisi", "tip": "int", "aciklama": "Eklenecek/çıkarılacak gün sayısı."},
    ],
    "ornek": 'DATE_TOOL(islem="simdi")',
    "kategori": "utility",
}


def run(islem: str = "simdi", tarih1: str = "", tarih2: str = "",
        hedef_format: str = "", gun_sayisi: int = 0, *args, **kwargs) -> str:
    """Tarih/saat işlemi yap.

    Args:
        islem: İşlem türü (simdi, formatla, fark, ekle, yilbasi, gun_bilgisi).
        tarih1: Birinci tarih.
        tarih2: İkinci tarih (fark için).
        hedef_format: Hedef format.
        gun_sayisi: Eklenecek/çıkarılacak gün.

    Returns:
        JSON: işlem sonucu.
    """
    if not islem:
        return json.dumps({"hata": "islem parametresi zorunludur."}, ensure_ascii=False)

    try:
        islem = islem.lower()

        if islem == "simdi":
            simdi = datetime.now()
            return json.dumps({
                "islem": "simdi",
                "tarih_saat": simdi.strftime("%Y-%m-%d %H:%M:%S"),
                "tarih": simdi.strftime("%Y-%m-%d"),
                "saat": simdi.strftime("%H:%M:%S"),
                "gun": simdi.strftime("%A"),
                "ay": simdi.strftime("%B"),
                "yil": simdi.year,
                "hafta_numarasi": simdi.isocalendar()[1],
                "unix_timestamp": int(simdi.timestamp()),
            }, ensure_ascii=False, indent=2)

        elif islem == "formatla":
            if not tarih1:
                return json.dumps({"hata": "tarih1 parametresi zorunludur."}, ensure_ascii=False)
            if not hedef_format:
                hedef_format = "%d.%m.%Y %H:%M:%S"

            # Otomatik format algılama
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S",
                        "%d.%m.%Y", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d",
                        "%m/%d/%Y", "%d/%m/%Y"]:
                try:
                    dt = datetime.strptime(tarih1, fmt)
                    break
                except ValueError:
                    continue
            else:
                return json.dumps({"hata": f"Tarih formatı taninamadi: {tarih1}"}, ensure_ascii=False)

            return json.dumps({
                "islem": "formatla",
                "giris": tarih1,
                "hedef_format": hedef_format,
                "sonuc": dt.strftime(hedef_format),
            }, ensure_ascii=False, indent=2)

        elif islem == "fark":
            if not tarih1 or not tarih2:
                return json.dumps({"hata": "tarih1 ve tarih2 parametreleri zorunludur."}, ensure_ascii=False)

            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S",
                        "%d.%m.%Y", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"]:
                try:
                    dt1 = datetime.strptime(tarih1, fmt)
                    dt2 = datetime.strptime(tarih2, fmt)
                    break
                except ValueError:
                    continue
            else:
                return json.dumps({"hata": "Tarih formatlari taninamadi."}, ensure_ascii=False)

            fark = dt2 - dt1 if dt2 > dt1 else dt1 - dt2

            return json.dumps({
                "islem": "fark",
                "tarih1": tarih1,
                "tarih2": tarih2,
                "fark_gun": fark.days,
                "fark_saat": fark.total_seconds() / 3600,
                "fark_dakika": fark.total_seconds() / 60,
                "fark_saniye": int(fark.total_seconds()),
            }, ensure_ascii=False, indent=2)

        elif islem == "ekle":
            if not tarih1:
                tarih1 = datetime.now().strftime("%Y-%m-%d")
            if gun_sayisi == 0:
                return json.dumps({"hata": "gun_sayisi parametresi gerekli."}, ensure_ascii=False)

            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S",
                        "%d.%m.%Y", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(tarih1, fmt)
                    break
                except ValueError:
                    continue
            else:
                return json.dumps({"hata": f"Tarih formatı taninamadi: {tarih1}"}, ensure_ascii=False)

            yeni_dt = dt + timedelta(days=gun_sayisi)

            return json.dumps({
                "islem": "ekle",
                "giris": tarih1,
                "eklenen_gun": gun_sayisi,
                "yeni_tarih": yeni_dt.strftime("%Y-%m-%d"),
                "yeni_gun": yeni_dt.strftime("%A"),
            }, ensure_ascii=False, indent=2)

        elif islem == "yilbasi":
            simdi = datetime.now()
            yilbasi = datetime(simdi.year + 1, 1, 1)
            kalan = yilbasi - simdi
            return json.dumps({
                "islem": "yilbasi",
                "yil": simdi.year + 1,
                "kalan_gun": kalan.days,
                "kalan_saat": int(kalan.total_seconds() / 3600),
                "kalan_dakika": int(kalan.total_seconds() / 60),
                "kalan_saniye": int(kalan.total_seconds()),
            }, ensure_ascii=False, indent=2)

        elif islem == "gun_bilgisi":
            if not tarih1:
                tarih1 = datetime.now().strftime("%Y-%m-%d")

            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d.%m.%Y %H:%M:%S",
                        "%d.%m.%Y", "%Y/%m/%d %H:%M:%S", "%Y/%m/%d"]:
                try:
                    dt = datetime.strptime(tarih1, fmt)
                    break
                except ValueError:
                    continue
            else:
                return json.dumps({"hata": f"Tarih formatı taninamadi: {tarih1}"}, ensure_ascii=False)

            return json.dumps({
                "islem": "gun_bilgisi",
                "tarih": tarih1,
                "gun_adi_tr": ["Pazartesi", "Sali", "Carsamba", "Persembe", "Cuma", "Cumartesi", "Pazar"][dt.weekday()],
                "gun_adi_en": dt.strftime("%A"),
                "ay_adi": dt.strftime("%B"),
                "yil": dt.year,
                "hafta_numarasi": dt.isocalendar()[1],
                "yilin_kacinci_gunu": dt.timetuple().tm_yday,
                "artik_yil": dt.year % 4 == 0 and (dt.year % 100 != 0 or dt.year % 400 == 0),
                "unix_timestamp": int(dt.timestamp()),
            }, ensure_ascii=False, indent=2)

        else:
            return json.dumps({
                "hata": f"Geçersiz işlem: {islem}",
                "desteklenen": ["simdi", "formatla", "fark", "ekle", "yilbasi", "gun_bilgisi"],
            }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"hata": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    print("=== SIMDI ===")
    print(run("simdi"))

    print("\n=== FARK ===")
    print(run("fark", tarih1="2024-01-01", tarih2="2024-12-31"))

    print("\n=== EKLE ===")
    print(run("ekle", tarih1="2024-01-01", gun_sayisi=30))

    print("\n=== GUN BILGISI ===")
    print(run("gun_bilgisi", tarih1="2024-12-25"))
