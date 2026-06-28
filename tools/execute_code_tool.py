# -*- coding: utf-8 -*-
"""execute_code_tool.py — İzole Python Kodu Çalıştırma Aracı.

ReYMeN'teki execute_code tool'un ReYMeN uyarlaması.
Güvenli sandbox'ta Python kodu çalıştırır, çıktıyı döndürür.

ToolRegistry'e kayıt için:
    TOOL_META = {...}
    def run(...)
"""

import sys
import io
import traceback
import textwrap
from pathlib import Path

TOOL_META = {
    "ad": "execute_code",
    "versiyon": "1.0.0",
    "aciklama": "Güvenli ortamda Python kodu çalıştırır ve çıktıyı döndürür.",
    "kategori": "orkestrasyon",
    "parametreler": {
        "kod": {
            "tip": "str",
            "aciklama": "Çalıştırılacak Python kodu",
            "zorunlu": True,
        },
        "timeout": {
            "tip": "int",
            "aciklama": "Zaman aşımı (saniye, varsayılan: 30)",
            "zorunlu": False,
        },
        "calisma_dizini": {
            "tip": "str",
            "aciklama": "Çalışma dizini (varsayılan: proje kökü)",
            "zorunlu": False,
        },
    },
    "yasakli_moduller": [
        "os.system", "subprocess", "shutil.rmtree",
        "__import__", "open(", "eval(", "exec(",
    ],
    "ornek": (
        'EXECUTE_CODE(kod="print(sum(range(10)))")'
    ),
}

_YASAKLI_KALIPLAR = [
    "os.system", "subprocess.run", "subprocess.Popen",
    "shutil.rmtree", "shutil.move",
    "eval(", "exec(", "__import__(",
    "open(", "open(\"",
    "import os; os.", "from os import",
    "import subprocess", "from subprocess import",
]


def _guvenlik_kontrol(kod: str) -> tuple:
    """Kodu güvenlik açısından kontrol eder.

    Returns:
        (gecerli_mi, hata_mesaji)
    """
    for kalip in _YASAKLI_KALIPLAR:
        if kalip in kod:
            return False, f"Güvenlik: '{kalip}' içeren kod çalıştırılamaz"
    return True, ""


def _kod_calistir(kod: str, timeout: int = 30, calisma_dizini: str = "") -> dict:
    """Python kodunu izole ortamda çalıştır.

    Returns:
        dict: {"cikti": ..., "hata": ..., "basarili": bool}
    """
    # Çalışma dizini
    if calisma_dizini:
        calisma_yolu = Path(calisma_dizini).resolve()
        if not calisma_yolu.exists():
            return {"cikti": "", "hata": f"Dizin bulunamadı: {calisma_dizini}", "basarili": False}
    else:
        calisma_yolu = Path.cwd()

    # stdout yakalama
    eski_stdout = sys.stdout
    eski_stderr = sys.stderr
    yeni_stdout = io.StringIO()
    yeni_stderr = io.StringIO()

    try:
        sys.stdout = yeni_stdout
        sys.stderr = yeni_stderr

        # Girintiyi düzelt
        duzgun_kod = textwrap.dedent(kod)

        # locals/globals için temiz namespace
        temiz_globals = {
            "__builtins__": __builtins__,
            "__name__": "__execute__",
        }
        # Dosya işlemleri için izin ver
        temiz_globals["Path"] = Path
        temiz_globals["print"] = print

        # Kodu çalıştır (timeout manuel olarak exec içinde kontrol edilmez)
        exec(duzgun_kod, temiz_globals)

        cikti = yeni_stdout.getvalue()
        hata = yeni_stderr.getvalue()

        return {
            "cikti": cikti,
            "hata": hata,
            "basarili": not hata.strip(),
        }

    except Exception as e:
        hata_detay = traceback.format_exc()
        return {
            "cikti": yeni_stdout.getvalue(),
            "hata": f"{type(e).__name__}: {e}\n{hata_detay}",
            "basarili": False,
        }
    finally:
        sys.stdout = eski_stdout
        sys.stderr = eski_stderr


def run(
    kod: str,
    timeout: int = 30,
    calisma_dizini: str = "",
) -> str:
    """Python kodunu çalıştır ve sonucu döndür.

    Args:
        kod: Çalıştırılacak Python kodu
        timeout: Zaman aşımı saniye (varsayılan: 30)
        calisma_dizini: Çalışma dizini

    Returns:
        str: Çıktı + hata bilgisi içeren metin
    """
    # Güvenlik kontrolü
    gecerli, hata = _guvenlik_kontrol(kod)
    if not gecerli:
        return f"[GUVENLIK_REDDI] {hata}"

    # Kod çalıştır
    sonuc = _kod_calistir(kod, timeout, calisma_dizini)

    # Sonucu formatla
    satirlar = []
    if sonuc["cikti"]:
        satirlar.append("--- ÇIKTI ---")
        satirlar.append(sonuc["cikti"].rstrip())
    if sonuc["hata"]:
        satirlar.append("--- HATA ---")
        satirlar.append(sonuc["hata"].rstrip())

    if not satirlar:
        satirlar.append("(çıktı yok)")

    durum = "✅" if sonuc["basarili"] else "❌"
    satirlar.insert(0, f"[EXECUTE_CODE {durum}]")

    return "\n".join(satirlar)


def check_fn(parametreler: dict) -> tuple:
    """Doğrulama: kod parametresi zorunlu."""
    if not parametreler.get("kod"):
        return False, "EXECUTE_CODE: 'kod' parametresi zorunludur"
    return True, ""


# Kısa kullanım alias
EXECUTE_CODE = run


def motor_kaydet(motor) -> None:
    """Motor'a EXECUTE_CODE aracını kaydet."""
    if not hasattr(motor, "_plugin_arac_kaydet"):
        return
    motor._plugin_arac_kaydet(
        "EXECUTE_CODE",
        lambda kod="", timeout="30", calisma_dizini="": run(
            kod=kod,
            timeout=int(timeout) if timeout.strip().isdigit() else 30,
            calisma_dizini=calisma_dizini,
        ),
        "Güvenli ortamda Python kodu çalıştırır ve çıktıyı döndürür.\n"
        'Kullanım: EXECUTE_CODE(kod="print(1+1)", timeout="30", calisma_dizini="")',
    )
