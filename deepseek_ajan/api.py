"""DeepSeek API istemcisi."""
import os, sys

DEFAULT_MODEL = "deepseek-v4-flash"
API_BASE = "https://api.deepseek.com/v1"

def api_istek(messages, model=None, temperature=0.7, max_tokens=4096):
    try:
        from openai import OpenAI
    except ImportError:
        print("openai gerekli: pip install openai")
        sys.exit(1)
    api_key = os.environ.get("DEEPSEEK_API_KEY") or _dotenv_key()
    if not api_key:
        print("HATA: DEEPSEEK_API_KEY bulunamadi.")
        print("  .env dosyasina ekle")
        sys.exit(1)
    client = OpenAI(api_key=api_key, base_url=API_BASE)
    model = model or os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
    try:
        r = client.chat.completions.create(
            model=model, messages=messages,
            max_tokens=max_tokens, temperature=temperature)
        return r.choices[0].message.content.strip() or ""
    except Exception as e:
        return f"[API Hatasi] {e}"

def _dotenv_key():
    for p in [".env", os.path.expanduser("~/.deepseek_ajan/.env")]:
        if os.path.exists(p):
            with open(p) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPSEEK_API_KEY") and "=" in line:
                        _, _, val = line.partition("=")
                        key = val.strip()
                        if key.startswith(chr(39)) or key.startswith(chr(34)):
                            key = key[1:-1]
                        if key:
                            os.environ["DEEPSEEK_API_KEY"] = key
                            return key
    return ""
