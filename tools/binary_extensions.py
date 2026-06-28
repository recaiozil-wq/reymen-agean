"""
İkili dosya uzantı tespiti aracı.
Bilinen binary uzantıları kontrol eder, listeler veya ekler.
"""
import os

BILINEN_BINARY_UZANTILAR = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.dat',
    '.png', '.jpg', '.mp3', '.mp4', '.zip'
}


def run(islem='kontrol', dosya_adi=None, uzanti=None, **kwargs):
    """
    İkili dosya uzantı tespiti yapar.

    Parametreler:
        islem (str): 'kontrol', 'liste' veya 'ekle'
        dosya_adi (str): Kontrol edilecek dosya adı (islem=kontrol için)
        uzanti (str): Eklenecek uzantı (islem=ekle için)

    Returns:
        str: İşlem sonucu.
    """
    global BILINEN_BINARY_UZANTILAR

    try:
        if islem == 'liste':
            uzantilar = sorted(BILINEN_BINARY_UZANTILAR)
            return f"Bilinen binary uzantılar ({len(uzantilar)}):\n" + "\n".join(uzantilar)

        elif islem == 'ekle':
            if not uzanti:
                return "Hata: 'uzanti' parametresi zorunludur."
            if not uzanti.startswith('.'):
                uzanti = '.' + uzanti
            BILINEN_BINARY_UZANTILAR.add(uzanti.lower())
            return f"Uzantı eklendi: {uzanti}"

        elif islem == 'kontrol':
            if not dosya_adi:
                return "Hata: 'dosya_adi' parametresi zorunludur."
            _, ext = os.path.splitext(dosya_adi)
            ext = ext.lower()
            if ext in BILINEN_BINARY_UZANTILAR:
                return f"'{dosya_adi}' -> Binary dosya (uzantı: {ext})"
            else:
                return f"'{dosya_adi}' -> Metin/metin tabanlı dosya (uzantı: {ext})"

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'kontrol', 'liste' veya 'ekle' kullanın."

    except Exception as e:
        return f"Binary uzantı tespit hatası: {str(e)}"
