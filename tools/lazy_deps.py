"""
Tembel bağımlılık yükleme aracı.
İhtiyaç anında pip paketi kurar.
"""
import importlib
import os
import subprocess
import sys

_KURULU_PAKETLER = {}


def _pip_kur(paket_adi, versiyon=None):
    """pip ile paket kur."""
    if versiyon:
        spec = f"{paket_adi}=={versiyon}"
    else:
        spec = paket_adi
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', spec],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return True, f"'{spec}' başarıyla kuruldu."
        return False, f"Kurulum hatası: {result.stderr[:500]}"
    except subprocess.TimeoutExpired:
        return False, f"Kurulum zaman aşımı: {spec}"
    except Exception as e:
        return False, f"Kurulum hatası: {str(e)}"


def run(islem='kontrol', paket_adi=None, versiyon=None, **kwargs):
    """
    Tembel bağımlılık yükleme.

    Parametreler:
        islem (str): 'kontrol', 'kur', 'kaldir' veya 'liste'
        paket_adi (str): Paket adı
        versiyon (str): İsteğe bağlı versiyon

    Returns:
        str: İşlem sonucu.
    """
    global _KURULU_PAKETLER

    try:
        if islem == 'liste':
            if not _KURULU_PAKETLER:
                return "Henüz lazy_deps ile kurulmuş paket yok."
            liste = "\n".join([f"  - {p} (v{v or '?'})" for p, v in _KURULU_PAKETLER.items()])
            return f"Lazy_deps ile kurulan paketler:\n{liste}"

        elif islem == 'kontrol':
            if not paket_adi:
                return "Hata: 'paket_adi' parametresi zorunludur."
            try:
                importlib.import_module(paket_adi)
                return f"'{paket_adi}' zaten yüklü."
            except ImportError:
                return f"'{paket_adi}' yüklü değil."

        elif islem == 'kur':
            if not paket_adi:
                return "Hata: 'paket_adi' parametresi zorunludur."
            try:
                importlib.import_module(paket_adi)
                return f"'{paket_adi}' zaten yüklü."
            except ImportError:
                basarili, mesaj = _pip_kur(paket_adi, versiyon)
                if basarili:
                    _KURULU_PAKETLER[paket_adi] = versiyon
                return mesaj

        elif islem == 'kaldir':
            if not paket_adi:
                return "Hata: 'paket_adi' parametresi zorunludur."
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'uninstall', '-y', paket_adi],
                    capture_output=True, text=True, timeout=30
                )
                if paket_adi in _KURULU_PAKETLER:
                    del _KURULU_PAKETLER[paket_adi]
                return f"'{paket_adi}' kaldırıldı." if result.returncode == 0 else f"Kaldırma hatası: {result.stderr[:500]}"
            except Exception as e:
                return f"Kaldırma hatası: {str(e)}"

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'kontrol', 'kur', 'kaldir' veya 'liste' kullanın."

    except Exception as e:
        return f"Lazy deps hatası: {str(e)}"
