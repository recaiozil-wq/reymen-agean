"""
xAI HTTP istemci.
Grok API'sine bağlanma.
"""
import json
import os

_XAI_API_KEY = os.environ.get('XAI_API_KEY', '')
_XAI_BASE_URL = "https://api.x.ai/v1"
_REYMEN_XAI_USER_AGENT = "ReYMeN-Agent/1.0"


def resolve_xai_http_credentials() -> dict | None:
    """xAI HTTP kimlik bilgilerini dondur.

    Returns:
        dict: {'api_key': ...} veya None (anahtar yoksa)
    """
    key = os.environ.get('XAI_API_KEY', '')
    if key:
        return {"api_key": key}
    return None


def has_xai_credentials() -> bool:
    """xAI API anahtari var mi kontrol et."""
    return bool(os.environ.get('XAI_API_KEY', ''))


def ReYMeN_xai_user_agent() -> str:
    """ReYMeN xAI User-Agent string'i."""
    return _REYMEN_XAI_USER_AGENT


# ReYMeN uyumluluğu için alias
hermes_xai_user_agent = ReYMeN_xai_user_agent


def run(islem='sorgula', mesaj=None, model="grok-2", **kwargs):
    """
    xAI HTTP istemci (Grok API).

    Parametreler:
        islem (str): 'sorgula', 'modeller' veya 'bakiye'
        mesaj (str/list): Kullanıcı mesajı
        model (str): Model adı (varsayılan: 'grok-2')

    Returns:
        str: İşlem sonucu.
    """
    try:
        if islem == 'modeller':
            if not _XAI_API_KEY:
                return "Hata: XAI_API_KEY bulunamadı."
            try:
                import requests
                headers = {'Authorization': f'Bearer {_XAI_API_KEY}'}
                resp = requests.get(f"{_XAI_BASE_URL}/models", headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    modeller = [m['id'] for m in data.get('data', [])]
                    return f"xAI modelleri:\n" + "\n".join([f"  - {m}" for m in modeller])
                return f"API hatası: {resp.status_code} - {resp.text[:500]}"
            except ImportError:
                return "Uyarı: requests modülü yüklü değil."
            except Exception as e:
                return f"Model listesi hatası: {str(e)}"

        elif islem == 'bakiye':
            if not _XAI_API_KEY:
                return "Hata: XAI_API_KEY bulunamadı."
            # xAI'nin bakiye endpoint'i yok, key varlığını kontrol et
            return f"XAI_API_KEY: {'Mevcut' if _XAI_API_KEY else 'Bulunamadı'}\nModel: {model}\nNot: xAI bakiye sorgulama endpoint'i bulunmamaktadır."

        elif islem == 'sorgula':
            if not mesaj:
                return "Hata: 'mesaj' parametresi zorunludur."
            if not _XAI_API_KEY:
                return "Hata: XAI_API_KEY bulunamadı."

            try:
                import requests

                if isinstance(mesaj, str):
                    messages = [{"role": "user", "content": mesaj}]
                elif isinstance(mesaj, list):
                    messages = mesaj
                else:
                    messages = [{"role": "user", "content": str(mesaj)}]

                headers = {
                    'Authorization': f'Bearer {_XAI_API_KEY}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'model': model,
                    'messages': messages,
                    'max_tokens': kwargs.get('max_tokens', 1024)
                }
                resp = requests.post(
                    f"{_XAI_BASE_URL}/chat/completions",
                    json=payload, headers=headers, timeout=30
                )
                if resp.status_code == 200:
                    data = resp.json()
                    content = data['choices'][0]['message']['content']
                    return json.dumps({
                        'model': model,
                        'yanit': content,
                        'token_kullanimi': data.get('usage', {})
                    }, indent=2, ensure_ascii=False)
                return f"API hatası: {resp.status_code} - {resp.text[:1000]}"
            except ImportError:
                return "Uyarı: requests modülü yüklü değil."
            except Exception as e:
                return f"Sorgu hatası: {str(e)}"

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'sorgula', 'modeller' veya 'bakiye' kullanın."

    except Exception as e:
        return f"xAI HTTP hatası: {str(e)}"
