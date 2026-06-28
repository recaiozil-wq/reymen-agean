"""
Gateway için onay/soru mekanizması.
Gateway üzerinden kullanıcıya soru sorma ve yanıt bekleme.
"""
import json
import time
import uuid

_BEKLEYEN_SORULAR = {}


def run(islem='sor', soru=None, kanal='console', **kwargs):
    """
    Gateway onay/soru mekanizması.

    Parametreler:
        islem (str): 'sor', 'bekle', 'yanitla' veya 'iptal'
        soru (str): Sorulacak soru metni
        kanal (str): Kanal (varsayılan: 'console')

    Returns:
        str: İşlem sonucu.
    """
    global _BEKLEYEN_SORULAR

    try:
        if islem == 'sor':
            if not soru:
                return "Hata: 'soru' parametresi zorunludur."
            soru_id = str(uuid.uuid4())[:8]
            _BEKLEYEN_SORULAR[soru_id] = {
                'soru': soru,
                'kanal': kanal,
                'zaman': time.time(),
                'durum': 'bekliyor',
                'yanit': None
            }
            return json.dumps({
                'soru_id': soru_id,
                'soru': soru,
                'kanal': kanal,
                'durum': 'bekliyor',
                'mesaj': f'Soru gönderildi (ID: {soru_id}). Kullanıcı yanıtı bekleniyor.'
            }, indent=2, ensure_ascii=False)

        elif islem == 'bekle':
            if not _BEKLEYEN_SORULAR:
                return "Bekleyen soru bulunamadı."
            bekleyen = {}
            for sid, data in _BEKLEYEN_SORULAR.items():
                if data['durum'] == 'bekliyor':
                    bekleyen[sid] = data
            if not bekleyen:
                return "Bekleyen soru bulunamadı."
            return json.dumps(bekleyen, indent=2, ensure_ascii=False, default=str)

        elif islem == 'yanitla':
            soru_id = kwargs.get('soru_id')
            yanit = kwargs.get('yanit')
            if not soru_id or yanit is None:
                return "Hata: 'soru_id' ve 'yanit' parametreleri zorunludur."
            if soru_id not in _BEKLEYEN_SORULAR:
                return f"Hata: Soru ID '{soru_id}' bulunamadı."
            _BEKLEYEN_SORULAR[soru_id]['yanit'] = yanit
            _BEKLEYEN_SORULAR[soru_id]['durum'] = 'yanitlandi'
            return f"Soru {soru_id} yanıtlandı: {yanit}"

        elif islem == 'iptal':
            soru_id = kwargs.get('soru_id')
            if soru_id:
                if soru_id in _BEKLEYEN_SORULAR:
                    _BEKLEYEN_SORULAR[soru_id]['durum'] = 'iptal'
                    return f"Soru {soru_id} iptal edildi."
                return f"Hata: Soru ID '{soru_id}' bulunamadı."
            _BEKLEYEN_SORULAR.clear()
            return "Tüm bekleyen sorular iptal edildi."

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'sor', 'bekle', 'yanitla' veya 'iptal' kullanın."

    except Exception as e:
        return f"Gateway hatası: {str(e)}"
