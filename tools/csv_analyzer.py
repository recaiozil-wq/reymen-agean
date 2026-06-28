# -*- coding: utf-8 -*-
"""csv_analyzer.py — CSV dosya analizi aracı.

CSV dosyasını okuyup sütun sayısı, satır sayısı, veri tipleri gibi
analiz bilgilerini döndürür.
"""

import json
import os
from pathlib import Path

# Opsiyonel: pandas
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Opsiyonel: csv (built-in)
import csv


TOOL_META = {
    "aciklama": "CSV dosyasını analiz eder: sütun/veri tipleri, satır sayısı, istatistikler.",
    "parametreler": [
        {"ad": "dosya_yolu", "tip": "str", "aciklama": "CSV dosyasının yolu."},
        {"ad": "detayli", "tip": "bool", "aciklama": "Detaylı analiz yapılsın mı? (varsayılan: false)"},
        {"ad": "delimiter", "tip": "str", "aciklama": "CSV ayracı (varsayılan: ',')."},
    ],
    "ornek": 'CSV_ANALYZER("veri.csv", detayli=true)',
    "kategori": "data_processing",
}


def run(dosya_yolu: str = "", detayli: bool = False, delimiter: str = ",", *args, **kwargs) -> str:
    """CSV dosyasını analiz et.

    Args:
        dosya_yolu: CSV dosyasının yolu.
        detayli: Detaylı analiz (pandas ile) yapılsın mı?
        delimiter: CSV ayracı (varsayılan: virgül).

    Returns:
        JSON: analiz sonuçları.
    """
    if not dosya_yolu:
        return json.dumps({"hata": "dosya_yolu parametresi zorunludur."}, ensure_ascii=False)

    yol = Path(dosya_yolu)
    if not yol.exists():
        return json.dumps({"hata": f"Dosya bulunamadı: {dosya_yolu}"}, ensure_ascii=False)
    if not yol.is_file():
        return json.dumps({"hata": f"Bu bir dosya değil: {dosya_yolu}"}, ensure_ascii=False)

    try:
        boyut = yol.stat().st_size
    except OSError:
        boyut = -1

    # Önce built-in csv ile oku
    try:
        with open(yol, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)
    except Exception as e:
        return json.dumps({"hata": f"CSV okuma hatasi: {str(e)}"}, ensure_ascii=False)

    if not rows:
        return json.dumps({"hata": "CSV dosyasi bos."}, ensure_ascii=False)

    satir_sayisi = len(rows) - 1  # header hariç
    sutun_sayisi = len(rows[0])
    header = rows[0]

    sonuc = {
        "dosya": str(yol),
        "boyut_bytes": boyut,
        "satir_sayisi": satir_sayisi,
        "sutun_sayisi": sutun_sayisi,
        "header": header,
        "ilk_3_satir": rows[1:4] if len(rows) > 1 else [],
    }

    # Pandas ile detaylı analiz
    if detayli and HAS_PANDAS:
        try:
            df = pd.read_csv(yol, delimiter=delimiter, nrows=10000)
            tipler = {}
            for col in df.columns:
                tipler[col] = str(df[col].dtype)
            sonuc["veri_tipleri"] = tipler
            sonuc["bos_deger_sayisi"] = df.isnull().sum().to_dict()
            sonuc["benzersiz_sayisi"] = {str(k): int(v) for k, v in df.nunique().to_dict().items()}

            # Sayısal sütunlar için istatistik
            istatistik = {}
            for col in df.select_dtypes(include=["number"]).columns:
                istatistik[col] = {
                    "min": float(df[col].min()) if pd.notna(df[col].min()) else None,
                    "max": float(df[col].max()) if pd.notna(df[col].max()) else None,
                    "ortalama": round(float(df[col].mean()), 2) if pd.notna(df[col].mean()) else None,
                }
            if istatistik:
                sonuc["istatistik"] = istatistik
        except Exception as e:
            sonuc["pandas_uyari"] = f"Pandas analizi basarisiz: {str(e)}"

    elif detayli and not HAS_PANDAS:
        sonuc["uyari"] = "Detayli analiz icin pandas kurulu olmali: pip install pandas"

    return json.dumps(sonuc, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write("ad,yas,sehir\nAli,30,Istanbul\nAyse,25,Ankara\nMehmet,35,Izmir\n")
        temp_path = f.name
    print(run(temp_path, detayli=False))
    os.unlink(temp_path)
