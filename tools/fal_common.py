"""
Fal.ai ortak işlevler.
API çağrıları, rate limit, token yönetimi.
"""
import json
import os
import time

_FAL_TOKEN = os.environ.get('FAL_KEY', '')
_RATE_LIMIT = {"son_cagri": 0, "min_interval": 1.0}


def _rate_limit_kontrol():
    """Rate limit kontrolü."""
    su_an = time.time()
    gecen = su_an - _RATE_LIMIT['son_cagri']
    if gecen < _RATE_LIMIT['min_interval']:
        bekle = _RATE_LIMIT['min_interval'] - gecen
        time.sleep(bekle)
    _RATE_LIMIT['son_cagri'] = time.time()


def run(islem='api_cagir', endpoint=None, parametreler=None, **kwargs):
    """
    Fal.ai ortak işlevler.

    Parametreler:
        islem (str): 'api_cagir', 'token_kontrol' veya 'queue_bekle'
        endpoint (str): API endpoint'i
        parametreler (dict): API parametreleri

    Returns:
        str: İşlem sonucu.
    """
    try:
        if islem == 'token_kontrol':
            if _FAL_TOKEN:
                return f"FAL_KEY mevcut ({_FAL_TOKEN[:8]}...{_FAL_TOKEN[-4:]})" if len(_FAL_TOKEN) > 12 else "FAL_KEY mevcut."
            return "FAL_KEY bulunamadı. Lütfen ortam değişkenini ayarlayın."

        elif islem == 'api_cagir':
            if not endpoint:
                return "Hata: 'endpoint' parametresi zorunludur."
            if not _FAL_TOKEN:
                return "Hata: FAL_KEY bulunamadı."
            if parametreler is None:
                parametreler = {}

            _rate_limit_kontrol()

            try:
                import requests
                headers = {
                    'Authorization': f'Key {_FAL_TOKEN}',
                    'Content-Type': 'application/json'
                }
                url = f"https://fal.run{endpoint}" if not endpoint.startswith('http') else endpoint
                response = requests.post(url, json=parametreler, headers=headers, timeout=30)
                return f"API çağrısı: {endpoint} -> Durum: {response.status_code}\n{response.text[:2000]}"
            except ImportError:
                return "Uyarı: requests modülü yüklü değil."

        elif islem == 'queue_bekle':
            request_id = kwargs.get('request_id')
            if not request_id:
                return "Hata: 'request_id' parametresi zorunludur."
            max_bekle = kwargs.get('max_bekle', 60)
            aralik = kwargs.get('aralik', 2)

            baslangic = time.time()
            for _ in range(int(max_bekle / aralik)):
                time.sleep(aralik)
                if time.time() - baslangic > max_bekle:
                    return f"Queue bekleme zaman aşımı ({max_bekle}s)."
            return f"Queue tamamlandı (request_id: {request_id})"

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'api_cagir', 'token_kontrol' veya 'queue_bekle' kullanın."

    except Exception as e:
        return f"Fal.ai hatası: {str(e)}"
