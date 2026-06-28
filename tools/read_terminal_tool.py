"""
Terminal çıktısı okuma aracı.
Terminal buffer'ından belirli satırları okuma.
"""
import os

# Bellek içi terminal buffer simülasyonu
_TERMINAL_BUFFER = []


def run(islem='son_n', n=20, baslangic=1, bitis=20, desen=None, **kwargs):
    """
    Terminal çıktısı okuma.

    Parametreler:
        islem (str): 'son_n', 'basla_bit', 'tumu' veya 'ara'
        n (int): Son n satır (varsayılan: 20)
        baslangic (int): Başlangıç satırı (varsayılan: 1)
        bitis (int): Bitiş satırı (varsayılan: 20)
        desen (str): Aranacak desen (regex)

    Returns:
        str: Okunan satırlar.
    """
    global _TERMINAL_BUFFER

    try:
        buffer_boyut = len(_TERMINAL_BUFFER)

        if islem == 'tumu':
            if buffer_boyut == 0:
                return "Terminal buffer'ı boş."
            satirlar = _TERMINAL_BUFFER
            return f"Terminal buffer ({buffer_boyut} satır):\n" + "\n".join(
                [f"{i + 1}|{l}" for i, l in enumerate(satirlar)]
            )

        elif islem == 'son_n':
            n = n or 20
            if buffer_boyut == 0:
                return "Terminal buffer'ı boş."
            basla = max(0, buffer_boyut - n)
            satirlar = _TERMINAL_BUFFER[basla:]
            return f"Son {len(satirlar)} satır:\n" + "\n".join(
                [f"{basla + i + 1}|{l}" for i, l in enumerate(satirlar)]
            )

        elif islem == 'basla_bit':
            baslangic = max(1, baslangic)
            bitis = min(buffer_boyut, bitis)
            if baslangic > buffer_boyut:
                return f"Hata: Başlangıç satırı ({baslangic}) buffer boyutundan ({buffer_boyut}) büyük."
            satirlar = _TERMINAL_BUFFER[baslangic - 1:bitis]
            return f"Satır {baslangic}-{bitis}:\n" + "\n".join(
                [f"{baslangic + i}|{l}" for i, l in enumerate(satirlar)]
            )

        elif islem == 'ara':
            if not desen:
                return "Hata: 'desen' parametresi zorunludur."
            import re
            try:
                pattern = re.compile(desen)
            except re.error as e:
                return f"Regex hatası: {e}"

            eslesmeler = []
            for i, satir in enumerate(_TERMINAL_BUFFER):
                if pattern.search(satir):
                    eslesmeler.append((i + 1, satir))

            if not eslesmeler:
                return f"'{desen}' için eşleşme bulunamadı."
            return f"'{desen}' için {len(eslesmeler)} eşleşme:\n" + "\n".join(
                [f"{no}|{l}" for no, l in eslesmeler]
            )

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'son_n', 'basla_bit', 'tumu' veya 'ara' kullanın."

    except Exception as e:
        return f"Terminal okuma hatası: {str(e)}"


def _buffer_ekle(veri):
    """Terminal buffer'ına veri ekle (iç kullanım)."""
    global _TERMINAL_BUFFER
    if isinstance(veri, str):
        satirlar = veri.split('\n')
    elif isinstance(veri, list):
        satirlar = veri
    else:
        satirlar = [str(veri)]
    _TERMINAL_BUFFER.extend(satirlar)
    # Maksimum 10000 satır tut
    if len(_TERMINAL_BUFFER) > 10000:
        _TERMINAL_BUFFER = _TERMINAL_BUFFER[-10000:]
