
> **Kategori:** AI_ML

---

## 📋 5N1K

| Soru | Cevap |
|:-----|:------|
| **Kim?** | Tüm ajanlar |
| **Ne?** | Ecc_Data Scraper Agent_References_Ai Client Py |
| **Nerede?** | AI_ML/ |
| **Ne Zaman?** | İhtiyaç duyulduğunda |
| **Neden?** | Otomatik kategorilendirme |
| **Nasıl?** | Skill referansı ile |

---

# ai/client.py
import os, json, time, requests

_last_call = 0.0

MODEL_FALLBACK = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-flash-lite-latest",
]


def generate(prompt: str, model: str = "", rate_limit: float = 7.0) -> dict:
    """Call Gemini with auto-fallback on 429. Returns parsed JSON or {}."""
    global _last_call

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return {}

    elapsed = time.time() - _last_call
    if elapsed < rate_limit:
        time.sleep(rate_limit - elapsed)

    models = [model] + [m for m in MODEL_FALLBACK if m != model] if model else MODEL_FALLBACK
    _last_call = time.time()

    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
                "maxOutputTokens": 2048,
            },
        }
        try:
            resp = requests.post(url, json=payload, timeout=30)
            if resp.status_code == 200:
                return _parse(resp)
            if resp.status_code in (429, 404):
                time.sleep(1)
                continue
            return {}
        except requests.RequestException:
            return {}

    return {}


def _parse(resp) -> dict:
    try:
        text = (
            resp.json()
            .get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)
    except (json.JSONDecodeError, KeyError):
        return {}
```

---

### Step 5: Build the AI Pipeline (Batch)

```python