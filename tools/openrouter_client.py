"""
OpenRouter API istemci.
Birden çok modeli OpenRouter üzerinden çağırma.
"""
import json
import os

_OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '')
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def run(islem='sorgula', model=None, mesaj=None, **kwargs):
    """
    OpenRouter API istemci.

    Parametreler:
        islem (str): 'sorgula', 'modeller' veya 'token'
        model (str): Model adı (örn: 'openai/gpt-4o')
        mesaj (str/list): Kullanıcı mesajı veya mesaj listesi

    Returns:
        str: İşlem sonucu.
    """
    try:
        if islem == 'modeller':
            if not _OPENROUTER_API_KEY:
                return "Hata: OPENROUTER_API_KEY bulunamadı."
            try:
                import requests
                headers = {'Authorization': f'Bearer {_OPENROUTER_API_KEY}'}
                resp = requests.get(f"{_OPENROUTER_BASE_URL}/models", headers=headers, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    models = data.get('data', [])
                    liste = "\n".join([f"  - {m['id']}" for m in models[:30]])
                    return f"OpenRouter modelleri ({len(models)} toplam):\n{liste}"
                return f"API hatası: {resp.status_code} - {resp.text[:500]}"
            except ImportError:
                return "Uyarı: requests modülü yüklü değil."
            except Exception as e:
                return f"Model listesi hatası: {str(e)}"

        elif islem == 'sorgula':
            if not model:
                model = "openai/gpt-4o-mini"
            if not mesaj:
                return "Hata: 'mesaj' parametresi zorunludur."
            if not _OPENROUTER_API_KEY:
                return "Hata: OPENROUTER_API_KEY bulunamadı."

            try:
                import requests

                if isinstance(mesaj, str):
                    messages = [{"role": "user", "content": mesaj}]
                elif isinstance(mesaj, list):
                    messages = mesaj
                else:
                    messages = [{"role": "user", "content": str(mesaj)}]

                headers = {
                    'Authorization': f'Bearer {_OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json'
                }
                payload = {
                    'model': model,
                    'messages': messages,
                    'max_tokens': kwargs.get('max_tokens', 1024)
                }
                resp = requests.post(
                    f"{_OPENROUTER_BASE_URL}/chat/completions",
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

        elif islem == 'token':
            return f"OPENROUTER_API_KEY: {'Mevcut' if _OPENROUTER_API_KEY else 'Bulunamadı'}"

        else:
            return f"Hata: Geçersiz işlem '{islem}'. 'sorgula', 'modeller' veya 'token' kullanın."

    except Exception as e:
        return f"OpenRouter hatası: {str(e)}"
