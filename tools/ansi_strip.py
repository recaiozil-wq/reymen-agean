"""
ANSI renk kodlarını temizleme aracı.
Regex ile \x1b[...m desenlerini kaldırır.
"""
import re

ANSI_PATTERN = re.compile(r'\x1b\[[0-9;]*m')


def run(metin=None, **kwargs):
    """
    ANSI renk kodlarını temizler.

    Parametreler:
        metin (str, zorunlu): Temizlenecek metin.

    Returns:
        str: ANSI kodlarından arındırılmış metin.
    """
    try:
        if metin is None:
            metin = kwargs.get('metin')
        if metin is None:
            return "Hata: 'metin' parametresi zorunludur."

        temiz_metin = ANSI_PATTERN.sub('', str(metin))
        return temiz_metin
    except Exception as e:
        return f"ANSI temizleme hatası: {str(e)}"
