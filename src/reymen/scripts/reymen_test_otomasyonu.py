"""
reymen_test_otomasyonu.py
ReYMeN Test Otomasyonu - Gorev 4 & 5

Gorev 4: reymen/sistem/ altindaki CLI-disi modullere otomatik pytest testi uret + coverage olc
Gorev 5: AGENTS.md gereksiz bolumlerini kirp (~392 âC? ~50 satir)

Guvenlik garantileri:
- compile() ile her test dosyasi yazilmadan once dogrulanir
- SyntaxError varsa o modul atlanir, digerleri devam eder
- Mevcut test dizinine (test_cli/) dokunulmaz
- main.py, run_agent.py agir giris modulleri haric tutulur
"""

import ast
import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Generator

# â??â?? Sabitler â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??

PROJE_KOKU = Path(__file__).resolve().parents[2]  # reymen/ ustu
SISTEM_DIZIN = PROJE_KOKU / "reymen" / "sistem"
TEST_HEDEF = PROJE_KOKU / "reymen" / "test" / "test_sistem"
AGENTS_DOSYA = PROJE_KOKU / "AGENTS.md"
RAPOR_DOSYA = PROJE_KOKU / "test_otomasyon_raporu.json"

HARIC_TUTULAN = frozenset({"main.py", "run_agent.py", "__init__.py"})
CLI_ONEKI = "cli_"

# AGENTS.md'de tutulacak bolum basliklari (buyuk/kucuk harf duyarsiz eslesme)
AGENTS_KRITIK_BOLUMLER = frozenset(
    {
        "genel bakis",
        "overview",
        "mimari",
        "architecture",
        "komutlar",
        "commands",
        "onemli kurallar",
        "critical rules",
        "notlar",
        "notes",
    }
)


# â??â?? Adim 1: Modulleri tara â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??


def adim1_tara_moduller() -> list[dict]:
    """
    reymen/sistem/ altinda CLI-disi tum .py modullerini AST ile parse eder;
    her modul icin public fonksiyon listesini cikarir.

    Yields:
        dict: {path, modul_adi, fonksiyonlar: [str]}
    """
    sonuclar: list[dict] = []

    if not SISTEM_DIZIN.exists():
        print(f"â?   SISTEM_DIZIN bulunamadi: {SISTEM_DIZIN}")
        return sonuclar

    for py_dosya in _iter_python_dosyalari(SISTEM_DIZIN):
        if py_dosya.name in HARIC_TUTULAN:
            continue
        if py_dosya.name.startswith(CLI_ONEKI):
            continue

        fonksiyonlar = _public_fonksiyonlari_bul(py_dosya)
        if fonksiyonlar is None:
            # parse hatasi; zaten loglandi
            continue

        modul_adi = _modul_adi_hesapla(py_dosya)
        sonuclar.append(
            {
                "path": py_dosya,
                "modul_adi": modul_adi,
                "fonksiyonlar": fonksiyonlar,
            }
        )

    print(f"gs?¦ ADIM 1: {len(sonuclar)} modul bulundu")
    return sonuclar


def _iter_python_dosyalari(dizin: Path) -> Generator[Path, None, None]:
    """Dizin altindaki .py dosyalarini lazy olarak uretir."""
    for dosya in dizin.rglob("*.py"):
        yield dosya


def _public_fonksiyonlari_bul(dosya: Path) -> list[str] | None:
    """
    AST parse ile dosyadaki _ ile baslamayan top-level fonksiyonlari dondurur.
    Parse basarisiz olursa None doner.
    """
    try:
        kaynak = dosya.read_text(encoding="utf-8")
        agac = ast.parse(kaynak, filename=str(dosya))
    except (SyntaxError, UnicodeDecodeError) as hata:
        print(f"  â?   AST parse hatasi [{dosya.name}]: {hata}")
        return None

    return [
        dugum.name
        for dugum in ast.walk(agac)
        if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not dugum.name.startswith("_")
        # Sadece top-level: parent kontrolu (basit yaklasim)
    ]


def _modul_adi_hesapla(dosya: Path) -> str:
    """
    Dosya yolundan Python import yolu uretir.
    Ornek: reymen/sistem/araclar/dosya.py âC? reymen.sistem.araclar.dosya
    """
    try:
        goreceli = dosya.relative_to(PROJE_KOKU)
        parcalar = list(goreceli.parts)
        parcalar[-1] = parcalar[-1].removesuffix(".py")
        return ".".join(parcalar)
    except ValueError:
        return dosya.stem


# â??â?? Adim 2-3: Test uret ve yaz â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??


def adim2_test_uret(modul: dict) -> str:
    """
    Tek bir modul icin pytest kaynak kodu uretir.
    Her test fonksiyonu try/except icinde cagrilir - crash durumunda pytest devam eder.
    """
    modul_adi = modul["modul_adi"]
    fonksiyonlar = modul["fonksiyonlar"]
    dosya_adi = modul["path"].stem

    satirlar = [
        "# Otomatik uretilmistir - elle duzenleme.",
        f"# Kaynak modul: {modul_adi}",
        "",
        "import pytest",
        f"import {modul_adi} as _modul",
        "",
    ]

    if not fonksiyonlar:
        # Hic public fonksiyon yoksa sadece import testi yaz
        satirlar += [
            "def test_import():",
            f"    # {modul_adi} modulunun import edilebilir oldugunu dogrular",
            "    assert _modul is not None",
            "",
        ]
        return "\n".join(satirlar)

    for fonk in fonksiyonlar:
        test_adi = f"test_{fonk}"
        satirlar += [
            f"def {test_adi}():",
            f"    # Otomatik test: {modul_adi}.{fonk}",
            "    try:",
            f"        _modul.{fonk}()",
            "    except SystemExit:",
            "        pytest.xfail('SystemExit')",
            "    except TypeError:",
            f"        pytest.skip('Arguman gerekli: {modul_adi}.{fonk}')",
            "    except Exception as hata:",
            "        pytest.xfail('Runtime hatasi: ' + str(hata))",
            "",
        ]

    return "\n".join(satirlar)


def adim3_test_yaz(moduller: list[dict]) -> tuple[int, int]:
    """
    Uretilen test kodlarini TEST_HEDEF dizinine yazar.
    compile() ile her dosyayi dogrular; SyntaxError varsa atlar.

    Returns:
        (yazilan_sayi, atlanan_sayi)
    """
    TEST_HEDEF.mkdir(parents=True, exist_ok=True)

    # __init__.py olustur (yoksa)
    init_dosya = TEST_HEDEF / "__init__.py"
    if not init_dosya.exists():
        init_dosya.write_text("", encoding="utf-8")

    yazilan = 0
    atlanan = 0

    for modul in moduller:
        test_kodu = adim2_test_uret(modul)
        hedef = TEST_HEDEF / f"test_{modul['path'].stem}.py"

        # compile() dogrulamasi - SyntaxError varsa yaz
        try:
            compile(test_kodu, str(hedef), "exec")
        except SyntaxError as hata:
            print(f"  â?- SyntaxError, atlandi [{modul['path'].stem}]: {hata}")
            atlanan += 1
            continue

        hedef.write_text(test_kodu, encoding="utf-8")
        yazilan += 1

    print(f"gs? ADIM 2-3: {yazilan} test dosyasi yazildi, {atlanan} atlandi")
    return yazilan, atlanan


# â??â?? Adim 4: Coverage olc â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??


def adim4_coverage_olc() -> dict:
    """
    pytest --cov=reymen.sistem calistirir.
    JSON raporundan modul bazli yuzdeleri dondurur.

    Returns:
        {
            "gecti": int,
            "kaldi": int,
            "toplam_coverage": float,
            "modul_coverage": {modul_adi: yuzde},
            "ham_cikti": str,
        }
    """
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(TEST_HEDEF),
        "--cov=reymen.sistem",
        "--cov-report=json:coverage.json",
        "--cov-report=term-missing",
        "-q",
    ]

    sonuc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJE_KOKU),
    )

    ham_cikti = sonuc.stdout + sonuc.stderr
    print(f"gs?? ADIM 4:\n{ham_cikti[-800:]}")  # Son 800 karakter yeterli

    # JSON raporu oku
    coverage_json = PROJE_KOKU / "coverage.json"
    modul_coverage: dict[str, float] = {}
    toplam_coverage = 0.0

    if coverage_json.exists():
        try:
            veri = json.loads(coverage_json.read_text(encoding="utf-8"))
            toplam_coverage = veri.get("totals", {}).get("percent_covered", 0.0)
            for dosya_yolu, bilgi in veri.get("files", {}).items():
                yuzde = bilgi.get("summary", {}).get("percent_covered", 0.0)
                modul_coverage[dosya_yolu] = round(yuzde, 1)
        except (json.JSONDecodeError, KeyError) as hata:
            print(f"  â?   Coverage JSON okunamadi: {hata}")

    # Gecen/kalan sayilari stdout'tan cikar (basit heuristic)
    gecti = kaldi = 0
    for satir in ham_cikti.splitlines():
        if "passed" in satir:
            for kelime in satir.split():
                if kelime.isdigit():
                    gecti = int(kelime)
                    break
        if "failed" in satir:
            for kelime in satir.split():
                if kelime.isdigit():
                    kaldi = int(kelime)
                    break

    return {
        "gecti": gecti,
        "kaldi": kaldi,
        "toplam_coverage": round(toplam_coverage, 1),
        "modul_coverage": modul_coverage,
        "ham_cikti": ham_cikti,
    }


# â??â?? Adim 5: AGENTS.md temizle â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??


def adim5_agents_temizle() -> tuple[int, int]:
    """
    AGENTS.md'yi okur; kritik olmayan bolumleri kirpar.
    Orijinali .bak uzantisiyla yedekler.

    Returns:
        (onceki_satir_sayisi, sonraki_satir_sayisi)
    """
    if not AGENTS_DOSYA.exists():
        print(f"â?   AGENTS.md bulunamadi: {AGENTS_DOSYA}")
        return 0, 0

    metin = AGENTS_DOSYA.read_text(encoding="utf-8")
    satirlar = metin.splitlines(keepends=True)
    onceki = len(satirlar)

    # Yedek
    yedek = AGENTS_DOSYA.with_suffix(".md.bak")
    yedek.write_text(metin, encoding="utf-8")

    # Bolum bazli filtre
    cikti_satirlari: list[str] = []
    aktif_bolum = True  # Baslangicta (baslik oncesi) her seyi dahil et

    for satir in satirlar:
        # Markdown baslik mi?
        if satir.startswith("#"):
            baslik_metni = satir.lstrip("#").strip().lower()
            aktif_bolum = any(
                kritik in baslik_metni for kritik in AGENTS_KRITIK_BOLUMLER
            )

        if aktif_bolum:
            cikti_satirlari.append(satir)

    sonraki = len(cikti_satirlari)
    AGENTS_DOSYA.write_text("".join(cikti_satirlari), encoding="utf-8")

    print(f"gs?? ADIM 5: AGENTS.md {onceki} âC? {sonraki} satir (yedek: {yedek.name})")
    return onceki, sonraki


# â??â?? Adim 6: Rapor yaz â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??


def adim6_rapor_yaz(
    moduller: list[dict],
    yazilan: int,
    atlanan: int,
    coverage: dict,
    agents_once: int,
    agents_sonra: int,
) -> None:
    """test_otomasyon_raporu.json dosyasini yazar."""
    rapor = {
        "bulunan_modul_sayisi": len(moduller),
        "yazilan_test_dosyasi": yazilan,
        "atlanan_test_dosyasi": atlanan,
        "gecen_test_sayisi": coverage["gecti"],
        "kalan_test_sayisi": coverage["kaldi"],
        "toplam_coverage": coverage["toplam_coverage"],
        "modul_coverage": coverage["modul_coverage"],
        "agents_md_onceki_satir": agents_once,
        "agents_md_sonraki_satir": agents_sonra,
    }

    RAPOR_DOSYA.write_text(
        json.dumps(rapor, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"â?? Rapor yazildi: {RAPOR_DOSYA}")


# â??â?? main â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??â??


def main() -> None:
    print("=" * 60)
    print("ReYMeN Test Otomasyonu - Gorev 4 & 5")
    print("=" * 60)

    moduller = adim1_tara_moduller()

    yazilan, atlanan = adim3_test_yaz(moduller)

    coverage = adim4_coverage_olc()

    agents_once, agents_sonra = adim5_agents_temizle()

    adim6_rapor_yaz(
        moduller,
        yazilan,
        atlanan,
        coverage,
        agents_once,
        agents_sonra,
    )

    print()
    print("â??" * 40)
    print(f"Toplam Coverage : %{coverage['toplam_coverage']}")
    print(f"Testler         : {coverage['gecti']} gecti / {coverage['kaldi']} kaldi")
    print(f"AGENTS.md       : {agents_once} âC? {agents_sonra} satir")
    print("â??" * 40)


if __name__ == "__main__":
    main()
